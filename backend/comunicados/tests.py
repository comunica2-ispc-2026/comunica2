"""Tests de comunicados — HU-07 (emisión + fan-out) + HU-08 (bandeja + acuse).

`APITestCase` sobre DB de test aislada.
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
        Vinculo.objects.create(usuario=self.mama, alumno=self.ana)
        Vinculo.objects.create(usuario=self.papa, alumno=self.ana)
        Vinculo.objects.create(usuario=self.mama, alumno=self.ben)

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

    def test_emision_seccion_hace_fanout(self):
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "Reunión", "cuerpo": "c", "tipo_destino": "SECCION", "seccion": self.sec.id},
            format="json",
        )
        com = Comunicado.objects.get(pk=r.json()["id"])
        self.assertEqual(com.entregas.count(), 3)
        self.assertEqual(r.json()["total_destinatarios"], 3)

    def test_emision_individual(self):
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "INDIVIDUAL", "alumno": self.ana.id},
            format="json",
        )
        com = Comunicado.objects.get(pk=r.json()["id"])
        self.assertEqual(com.entregas.count(), 2)

    def test_seccion_sin_seccion_400(self):
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "SECCION"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_individual_con_seccion_400(self):
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "INDIVIDUAL",
             "alumno": self.ana.id, "seccion": self.sec.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class AcuseTests(APITestCase):
    def setUp(self):
        self.emisor = Usuario.objects.create(username="61000001", dni="61000001", rol=Usuario.Rol.ADMINISTRADOR)
        self.mama = Usuario.objects.create(username="61000002", dni="61000002", rol=Usuario.Rol.FAMILIA)
        self.otra = Usuario.objects.create(username="61000003", dni="61000003", rol=Usuario.Rol.FAMILIA)
        self.sec = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3A", turno=Seccion.Turno.MANANA)
        self.ana = Alumno.objects.create(nombre="Ana", apellido="P", dni="71000001", seccion=self.sec)
        self.ben = Alumno.objects.create(nombre="Ben", apellido="Q", dni="71000002", seccion=self.sec)
        Vinculo.objects.create(usuario=self.mama, alumno=self.ana)
        Vinculo.objects.create(usuario=self.otra, alumno=self.ben)
        self.com = Comunicado.objects.create(
            emisor=self.emisor, tipo_destino=Comunicado.TipoDestino.SECCION, seccion=self.sec,
            titulo="Circular", cuerpo="c",
        )
        self.com.generar_entregas()

    def test_bandeja_filtrada_por_token(self):
        r = _cliente(self.mama).get("/api/mi-bandeja/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # mama solo ve su entrega (la de Ana), no la de la otra familia.
        alumnos = {e["alumno"] for e in r.json()["results"]}
        self.assertEqual(alumnos, {self.ana.id})

    def test_acusar_setea_fecha(self):
        entrega = EntregaComunicado.objects.get(familiar=self.mama, alumno=self.ana)
        r = _cliente(self.mama).post(f"/api/mi-bandeja/{entrega.id}/acusar/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        entrega.refresh_from_db()
        self.assertIsNotNone(entrega.acusado_en)

    def test_acuse_es_idempotente(self):
        entrega = EntregaComunicado.objects.get(familiar=self.mama, alumno=self.ana)
        c = _cliente(self.mama)
        c.post(f"/api/mi-bandeja/{entrega.id}/acusar/")
        entrega.refresh_from_db()
        primera = entrega.acusado_en
        c.post(f"/api/mi-bandeja/{entrega.id}/acusar/")
        entrega.refresh_from_db()
        self.assertEqual(entrega.acusado_en, primera)  # conserva el primer acuse

    def test_no_acusa_entrega_ajena(self):
        # La entrega de la otra familia no está en la bandeja de mama -> 404.
        ajena = EntregaComunicado.objects.get(familiar=self.otra, alumno=self.ben)
        r = _cliente(self.mama).post(f"/api/mi-bandeja/{ajena.id}/acusar/")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_requiere_acuse_400(self):
        com2 = Comunicado.objects.create(
            emisor=self.emisor, tipo_destino=Comunicado.TipoDestino.INDIVIDUAL, alumno=self.ana,
            titulo="FYI", cuerpo="c", requiere_acuse=False,
        )
        com2.generar_entregas()
        entrega = EntregaComunicado.objects.get(comunicado=com2, familiar=self.mama)
        r = _cliente(self.mama).post(f"/api/mi-bandeja/{entrega.id}/acusar/")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_total_acusados_refleja_el_acuse(self):
        entrega = EntregaComunicado.objects.get(familiar=self.mama, alumno=self.ana)
        _cliente(self.mama).post(f"/api/mi-bandeja/{entrega.id}/acusar/")
        r = _cliente(self.emisor).get(f"/api/comunicados/{self.com.id}/entregas/")
        acusados = [e for e in r.json() if e["acusado"]]
        self.assertEqual(len(acusados), 1)
