"""Tests de HU-04 — registro y gestión de alumnos.

`APITestCase` sobre DB de test aislada. Cubre:
- Acceso: admin lee/escribe; docente/autoridad leen; familia -> 403; sin token -> 401.
- Alta de alumno por el admin, con y sin sección (RF07).
- Filtro ?seccion=<id>.
- Baja lógica: DELETE apaga `activo` (no borra la fila).
"""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from usuarios.models import Usuario
from .models import Alumno, Seccion


def _cliente(user):
    from rest_framework.test import APIClient
    c = APIClient()
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        c.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return c


class AlumnosTests(APITestCase):
    def setUp(self):
        self.admin = Usuario.objects.create(username="40000001", dni="40000001", rol=Usuario.Rol.ADMINISTRADOR)
        self.docente = Usuario.objects.create(username="40000002", dni="40000002", rol=Usuario.Rol.DOCENTE)
        self.familia = Usuario.objects.create(username="40000003", dni="40000003", rol=Usuario.Rol.FAMILIA)
        self.sec = Seccion.objects.create(
            nivel=Seccion.Nivel.PRIMARIA, nombre="3A", turno=Seccion.Turno.MANANA
        )
        self.c_admin = _cliente(self.admin)
        self.c_docente = _cliente(self.docente)
        self.c_familia = _cliente(self.familia)
        self.c_anon = _cliente(None)

    def _payload(self, **kw):
        base = {"nombre": "Ana", "apellido": "Pérez", "dni": "50000001"}
        base.update(kw)
        return base

    # --- acceso ---
    def test_sin_token_401(self):
        self.assertEqual(self.c_anon.get("/api/alumnos/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_docente_lee_200(self):
        self.assertEqual(self.c_docente.get("/api/alumnos/").status_code, status.HTTP_200_OK)

    def test_familia_no_lee_403(self):
        # La familia no entra por este endpoint (usa mis-alumnos, HU-05).
        self.assertEqual(self.c_familia.get("/api/alumnos/").status_code, status.HTTP_403_FORBIDDEN)

    def test_docente_no_escribe_403(self):
        r = self.c_docente.post("/api/alumnos/", self._payload(), format="json")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    # --- alta ---
    def test_admin_crea_alumno_con_seccion(self):
        r = self.c_admin.post("/api/alumnos/", self._payload(seccion=self.sec.id), format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.json()["turno"], Seccion.Turno.MANANA)  # turno derivado de la sección

    def test_admin_crea_alumno_sin_seccion(self):
        # RF07: un alumno puede existir antes de ser asignado a una sección.
        r = self.c_admin.post("/api/alumnos/", self._payload(dni="50000009"), format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(r.json()["turno"])

    def test_dni_con_letras_400(self):
        r = self.c_admin.post("/api/alumnos/", self._payload(dni="ABC123"), format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    # --- filtro ---
    def test_filtro_por_seccion(self):
        Alumno.objects.create(nombre="Ben", apellido="Q", dni="50000002", seccion=self.sec)
        otra = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3B", turno=Seccion.Turno.TARDE)
        Alumno.objects.create(nombre="Cyn", apellido="R", dni="50000003", seccion=otra)
        r = self.c_admin.get(f"/api/alumnos/?seccion={self.sec.id}")
        dnis = {a["dni"] for a in r.json()["results"]}
        self.assertEqual(dnis, {"50000002"})

    # --- baja lógica ---
    def test_delete_es_baja_logica(self):
        alu = Alumno.objects.create(nombre="Dan", apellido="S", dni="50000004", seccion=self.sec)
        r = self.c_admin.delete(f"/api/alumnos/{alu.id}/")
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Alumno.objects.filter(id=alu.id, activo=False).exists())
