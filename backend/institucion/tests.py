"""Tests de #32 — alcance por objeto (institucion).

`APITestCase` sobre DB de test aislada. Dos bloques:
- Resolver (`alcance.py`): reduce cada rol a un set concreto de secciones/alumnos
  (admin/director/preceptor/docente/familia + tesorero por grupos). ORM directo.
- API de administración (admin-only): alta de las 4 entidades, reglas de rol del
  serializer, M2M de grupos, y control de acceso.

La emisión acotada por alcance (`destino_en_alcance`, tipo GRUPO) se prueba en la
fase 2 de comunicados (slice 7), cuando ese método existe.
"""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from alumnos.models import Alumno, Seccion, Vinculo
from institucion.alcance import alumnos_en_alcance, secciones_en_alcance
from institucion.models import (
    AlcanceAutoridad,
    AlcanceGrupo,
    AsignacionDocente,
    GrupoPersonalizado,
)
from usuarios.models import Usuario


def _cliente(user):
    c = APIClient()
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        c.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return c


def _nombres(qs):
    return sorted(qs.values_list("nombre", flat=True))


class ResolverTests(APITestCase):
    def setUp(self):
        self.prim_m = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3A", turno=Seccion.Turno.MANANA)
        self.prim_t = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3B", turno=Seccion.Turno.TARDE)
        self.sec_m = Seccion.objects.create(nivel=Seccion.Nivel.SECUNDARIA, nombre="1A", turno=Seccion.Turno.MANANA)

        self.admin = Usuario.objects.create(username="90000001", dni="90000001", rol=Usuario.Rol.ADMINISTRADOR)
        self.direc = Usuario.objects.create(username="90000002", dni="90000002", rol=Usuario.Rol.AUTORIDAD)
        self.prece = Usuario.objects.create(username="90000003", dni="90000003", rol=Usuario.Rol.AUTORIDAD)
        self.docen = Usuario.objects.create(username="90000004", dni="90000004", rol=Usuario.Rol.DOCENTE)
        self.fam = Usuario.objects.create(username="90000005", dni="90000005", rol=Usuario.Rol.FAMILIA)

        self.ana = Alumno.objects.create(nombre="Ana", apellido="X", dni="80000001", seccion=self.prim_m)
        self.ben = Alumno.objects.create(nombre="Ben", apellido="X", dni="80000002", seccion=self.prim_t)
        Vinculo.objects.create(usuario=self.fam, alumno=self.ana, parentesco=Vinculo.Parentesco.MADRE)

        AlcanceAutoridad.objects.create(autoridad=self.direc, nivel=Seccion.Nivel.PRIMARIA, turno=None)
        AlcanceAutoridad.objects.create(autoridad=self.prece, nivel=Seccion.Nivel.PRIMARIA, turno=Seccion.Turno.MANANA)
        AsignacionDocente.objects.create(docente=self.docen, seccion=self.prim_m)

    def test_admin_ve_todas(self):
        self.assertEqual(_nombres(secciones_en_alcance(self.admin)), ["1A", "3A", "3B"])

    def test_director_ve_su_nivel(self):
        self.assertEqual(_nombres(secciones_en_alcance(self.direc)), ["3A", "3B"])

    def test_preceptor_acota_turno(self):
        self.assertEqual(_nombres(secciones_en_alcance(self.prece)), ["3A"])

    def test_docente_ve_su_seccion(self):
        self.assertEqual(_nombres(secciones_en_alcance(self.docen)), ["3A"])

    def test_familia_sin_alcance_por_seccion(self):
        self.assertEqual(_nombres(secciones_en_alcance(self.fam)), [])

    def test_familia_ve_solo_su_hija(self):
        self.assertEqual(_nombres(alumnos_en_alcance(self.fam)), ["Ana"])

    def test_docente_ve_alumnos_de_su_seccion(self):
        self.assertEqual(_nombres(alumnos_en_alcance(self.docen)), ["Ana"])

    def test_director_ve_alumnos_de_su_nivel(self):
        self.assertEqual(_nombres(alumnos_en_alcance(self.direc)), ["Ana", "Ben"])


class ResolverGruposTests(APITestCase):
    def setUp(self):
        self.prim_m = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3A", turno=Seccion.Turno.MANANA)
        self.prim_t = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3B", turno=Seccion.Turno.TARDE)
        self.sec_m = Seccion.objects.create(nivel=Seccion.Nivel.SECUNDARIA, nombre="1A", turno=Seccion.Turno.MANANA)
        self.tesor = Usuario.objects.create(username="92000003", dni="92000003", rol=Usuario.Rol.AUTORIDAD)
        self.tesor_vacio = Usuario.objects.create(username="92000004", dni="92000004", rol=Usuario.Rol.AUTORIDAD)
        # grupo que cruza niveles (3A primaria + 1A secundaria)
        self.grupo = GrupoPersonalizado.objects.create(nombre="Mixto")
        self.grupo.secciones.set([self.prim_m, self.sec_m])
        AlcanceGrupo.objects.create(autoridad=self.tesor, grupo=self.grupo)

    def test_tesorero_ve_secciones_de_su_grupo(self):
        self.assertEqual(_nombres(secciones_en_alcance(self.tesor)), ["1A", "3A"])

    def test_tesorero_no_ve_seccion_fuera_del_grupo(self):
        self.assertNotIn("3B", _nombres(secciones_en_alcance(self.tesor)))

    def test_tesorero_sin_grupos_sin_alcance(self):
        self.assertEqual(_nombres(secciones_en_alcance(self.tesor_vacio)), [])


class InstitucionAPITests(APITestCase):
    def setUp(self):
        self.admin = Usuario.objects.create(username="95000001", dni="95000001", rol=Usuario.Rol.ADMINISTRADOR)
        self.docen = Usuario.objects.create(username="95000002", dni="95000002", rol=Usuario.Rol.DOCENTE)
        self.autor = Usuario.objects.create(username="95000003", dni="95000003", rol=Usuario.Rol.AUTORIDAD, cargo=Usuario.Cargo.DIRECTOR)
        self.fam = Usuario.objects.create(username="95000004", dni="95000004", rol=Usuario.Rol.FAMILIA)
        self.sec_a = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3A", turno=Seccion.Turno.MANANA)
        self.sec_b = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3B", turno=Seccion.Turno.TARDE)
        self.c_admin = _cliente(self.admin)
        self.c_docen = _cliente(self.docen)
        self.c_anon = _cliente(None)

    def test_asignacion_docente_valida(self):
        r = self.c_admin.post("/api/asignaciones-docente/", {"docente": self.docen.id, "seccion": self.sec_a.id}, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_asignacion_a_no_docente_400(self):
        r = self.c_admin.post("/api/asignaciones-docente/", {"docente": self.fam.id, "seccion": self.sec_a.id}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_alcance_autoridad_valido(self):
        r = self.c_admin.post("/api/alcances-autoridad/", {"autoridad": self.autor.id, "nivel": Seccion.Nivel.PRIMARIA}, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_alcance_a_no_autoridad_400(self):
        r = self.c_admin.post("/api/alcances-autoridad/", {"autoridad": self.docen.id, "nivel": Seccion.Nivel.PRIMARIA}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_grupo_con_secciones(self):
        r = self.c_admin.post("/api/grupos/", {"nombre": "Cuotas", "secciones": [self.sec_a.id, self.sec_b.id]}, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        grupo = GrupoPersonalizado.objects.get(nombre="Cuotas")
        self.assertEqual(set(grupo.secciones.values_list("id", flat=True)), {self.sec_a.id, self.sec_b.id})

    def test_alcance_grupo_valido(self):
        grupo = GrupoPersonalizado.objects.create(nombre="G")
        r = self.c_admin.post("/api/alcances-grupo/", {"autoridad": self.autor.id, "grupo": grupo.id}, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_docente_no_escribe_403(self):
        r = self.c_docen.post("/api/asignaciones-docente/", {"docente": self.docen.id, "seccion": self.sec_b.id}, format="json")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_docente_no_lee_403(self):
        self.assertEqual(self.c_docen.get("/api/asignaciones-docente/").status_code, status.HTTP_403_FORBIDDEN)

    def test_sin_token_401(self):
        self.assertEqual(self.c_anon.get("/api/grupos/").status_code, status.HTTP_401_UNAUTHORIZED)
