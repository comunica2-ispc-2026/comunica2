"""Tests de HU-07 — envío de comunicados (fase 1: broadcast + fan-out).

`APITestCase` sobre DB de test aislada. Cubre:
- Emisión por rol: admin/autoridad/docente emiten (201); familia -> 403; sin token -> 401.
- Fan-out on write: una entrega por cada familiar vinculado a cada alumno del destino.
- Destinos INDIVIDUAL y SECCION.
- Coherencia tipo<->localizador (400 si falta o sobra).
- Acción entregas/: estado de acuse (todas pendientes recién emitido).
"""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from alumnos.models import Alumno, Seccion, Vinculo
from usuarios.models import Usuario
from .models import Comunicado, EntregaComunicado


def _cliente(user):
    c = APIClient()
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        c.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return c


class EmisionTests(APITestCase):
    def setUp(self):
        self.admin = Usuario.objects.create(username="60000001", dni="60000001", rol=Usuario.Rol.ADMINISTRADOR)
        self.docente = Usuario.objects.create(username="60000002", dni="60000002", rol=Usuario.Rol.DOCENTE)
        self.familia = Usuario.objects.create(username="60000003", dni="60000003", rol=Usuario.Rol.FAMILIA)
        self.mama = Usuario.objects.create(username="60000004", dni="60000004", rol=Usuario.Rol.FAMILIA)
        self.papa = Usuario.objects.create(username="60000005", dni="60000005", rol=Usuario.Rol.FAMILIA)

        self.sec = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3A", turno=Seccion.Turno.MANANA)
        self.ana = Alumno.objects.create(nombre="Ana", apellido="P", dni="70000001", seccion=self.sec)
        self.ben = Alumno.objects.create(nombre="Ben", apellido="Q", dni="70000002", seccion=self.sec)
        # Ana tiene dos familiares vinculados; Ben uno.
        Vinculo.objects.create(usuario=self.mama, alumno=self.ana)
        Vinculo.objects.create(usuario=self.papa, alumno=self.ana)
        Vinculo.objects.create(usuario=self.mama, alumno=self.ben)

    # --- acceso ---
    def test_sin_token_401(self):
        self.assertEqual(_cliente(None).get("/api/comunicados/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_familia_no_emite_403(self):
        r = _cliente(self.familia).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "SECCION", "seccion": self.sec.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_docente_emite_201(self):
        r = _cliente(self.docente).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "SECCION", "seccion": self.sec.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    # --- fan-out ---
    def test_emision_seccion_hace_fanout(self):
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "Reunión", "cuerpo": "c", "tipo_destino": "SECCION", "seccion": self.sec.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        com = Comunicado.objects.get(pk=r.json()["id"])
        # Ana(mama+papa) + Ben(mama) = 3 entregas, grano (familiar, alumno).
        self.assertEqual(com.entregas.count(), 3)
        self.assertEqual(r.json()["total_destinatarios"], 3)
        self.assertEqual(r.json()["total_acusados"], 0)

    def test_emision_individual(self):
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "INDIVIDUAL", "alumno": self.ana.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        com = Comunicado.objects.get(pk=r.json()["id"])
        self.assertEqual(com.entregas.count(), 2)  # los dos familiares de Ana

    # --- coherencia tipo<->localizador ---
    def test_seccion_sin_seccion_400(self):
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "SECCION"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_individual_con_seccion_400(self):
        # Localizador que no corresponde al tipo.
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "INDIVIDUAL",
             "alumno": self.ana.id, "seccion": self.sec.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    # --- acción entregas/ ---
    def test_entregas_muestra_estado(self):
        com = Comunicado.objects.create(
            emisor=self.admin, tipo_destino=Comunicado.TipoDestino.INDIVIDUAL, alumno=self.ana,
            titulo="t", cuerpo="c",
        )
        com.generar_entregas()
        r = _cliente(self.admin).get(f"/api/comunicados/{com.id}/entregas/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.json()), 2)
        self.assertTrue(all(e["acusado"] is False for e in r.json()))
