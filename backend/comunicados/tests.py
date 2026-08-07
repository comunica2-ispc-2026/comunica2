"""Tests de comunicados — fase 1 (emisión + acuse) + fase 2 (alcance + categoría).

`APITestCase` sobre DB de test aislada. Los tests de fase-2 sobre
`destino_en_alcance` / `categoria_permitida` se hacen a nivel modelo (instancias
transitorias, como arma la vista antes de persistir) + un par a nivel API para
confirmar el 403 de la vista.
"""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from alumnos.models import Alumno, Seccion, Vinculo
from institucion.models import AlcanceAutoridad, AlcanceGrupo, AsignacionDocente, GrupoPersonalizado
from usuarios.models import Usuario
from .models import Comunicado, EntregaComunicado

T = Comunicado.TipoDestino
Cat = Comunicado.Categoria


def _cliente(user):
    c = APIClient()
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        c.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return c


def _com(tipo, categoria=Cat.ACADEMICO, **kw):
    """Comunicado transitorio (sin guardar), como el que arma la vista."""
    return Comunicado(tipo_destino=tipo, categoria=categoria, titulo="t", cuerpo="c", **kw)


# ============================ FASE 1 (emisión + acuse) ============================

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

    def test_familia_no_emite_403(self):
        r = _cliente(self.familia).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "SECCION", "seccion": self.sec.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_emite_seccion_fanout(self):
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "SECCION", "seccion": self.sec.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.json()["total_destinatarios"], 3)

    def test_seccion_sin_seccion_400(self):
        r = _cliente(self.admin).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "SECCION"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class AcuseTests(APITestCase):
    def setUp(self):
        self.emisor = Usuario.objects.create(username="61000001", dni="61000001", rol=Usuario.Rol.ADMINISTRADOR)
        self.mama = Usuario.objects.create(username="61000002", dni="61000002", rol=Usuario.Rol.FAMILIA)
        self.sec = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3A", turno=Seccion.Turno.MANANA)
        self.ana = Alumno.objects.create(nombre="Ana", apellido="P", dni="71000001", seccion=self.sec)
        Vinculo.objects.create(usuario=self.mama, alumno=self.ana)
        self.com = Comunicado.objects.create(
            emisor=self.emisor, tipo_destino=T.SECCION, seccion=self.sec, titulo="Circular", cuerpo="c",
        )
        self.com.generar_entregas()

    def test_acusar_setea_fecha_idempotente(self):
        entrega = EntregaComunicado.objects.get(familiar=self.mama, alumno=self.ana)
        c = _cliente(self.mama)
        r = c.post(f"/api/mi-bandeja/{entrega.id}/acusar/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        entrega.refresh_from_db()
        primera = entrega.acusado_en
        self.assertIsNotNone(primera)
        c.post(f"/api/mi-bandeja/{entrega.id}/acusar/")
        entrega.refresh_from_db()
        self.assertEqual(entrega.acusado_en, primera)


# ============================ FASE 2 (alcance + categoría) ============================

class AlcanceEmisionTests(APITestCase):
    """`destino_en_alcance`: destino ⊆ alcance del emisor (nivel modelo)."""

    def setUp(self):
        self.prim_m = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3A", turno=Seccion.Turno.MANANA)
        self.prim_t = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3B", turno=Seccion.Turno.TARDE)
        self.sec_m = Seccion.objects.create(nivel=Seccion.Nivel.SECUNDARIA, nombre="1A", turno=Seccion.Turno.MANANA)
        self.admin = Usuario.objects.create(username="91000001", dni="91000001", rol=Usuario.Rol.ADMINISTRADOR)
        self.direc = Usuario.objects.create(username="91000002", dni="91000002", rol=Usuario.Rol.AUTORIDAD)
        self.prece = Usuario.objects.create(username="91000003", dni="91000003", rol=Usuario.Rol.AUTORIDAD)
        self.docen = Usuario.objects.create(username="91000004", dni="91000004", rol=Usuario.Rol.DOCENTE)
        self.ana = Alumno.objects.create(nombre="Ana", apellido="X", dni="81000001", seccion=self.prim_m)
        self.ben = Alumno.objects.create(nombre="Ben", apellido="X", dni="81000002", seccion=self.prim_t)
        AlcanceAutoridad.objects.create(autoridad=self.direc, nivel=Seccion.Nivel.PRIMARIA, turno=None)
        AlcanceAutoridad.objects.create(autoridad=self.prece, nivel=Seccion.Nivel.PRIMARIA, turno=Seccion.Turno.MANANA)
        AsignacionDocente.objects.create(docente=self.docen, seccion=self.prim_m)

    def test_docente_su_seccion_si_ajena_no(self):
        self.assertTrue(_com(T.SECCION, seccion=self.prim_m).destino_en_alcance(self.docen))
        self.assertFalse(_com(T.SECCION, seccion=self.prim_t).destino_en_alcance(self.docen))

    def test_docente_individual(self):
        self.assertTrue(_com(T.INDIVIDUAL, alumno=self.ana).destino_en_alcance(self.docen))
        self.assertFalse(_com(T.INDIVIDUAL, alumno=self.ben).destino_en_alcance(self.docen))

    def test_preceptor_su_turno(self):
        self.assertTrue(_com(T.TURNO, nivel=Seccion.Nivel.PRIMARIA, turno=Seccion.Turno.MANANA).destino_en_alcance(self.prece))
        self.assertFalse(_com(T.TURNO, nivel=Seccion.Nivel.PRIMARIA, turno=Seccion.Turno.TARDE).destino_en_alcance(self.prece))

    def test_director_nivel_completo(self):
        self.assertTrue(_com(T.NIVEL, nivel=Seccion.Nivel.PRIMARIA).destino_en_alcance(self.direc))
        self.assertFalse(_com(T.NIVEL, nivel=Seccion.Nivel.SECUNDARIA).destino_en_alcance(self.direc))

    def test_escuela_solo_admin(self):
        self.assertFalse(_com(T.ESCUELA).destino_en_alcance(self.direc))
        self.assertTrue(_com(T.ESCUELA).destino_en_alcance(self.admin))

    def test_fanout_por_nivel(self):
        alcanzados = sorted(
            _com(T.NIVEL, nivel=Seccion.Nivel.PRIMARIA).alumnos_destinatarios().values_list("nombre", flat=True)
        )
        self.assertEqual(alcanzados, ["Ana", "Ben"])

    def test_vista_403_fuera_de_alcance(self):
        # A nivel API: el docente NO puede emitir a una sección ajena.
        r = _cliente(self.docen).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "SECCION", "seccion": self.prim_t.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_vista_201_en_alcance(self):
        r = _cliente(self.docen).post(
            "/api/comunicados/",
            {"titulo": "t", "cuerpo": "c", "tipo_destino": "SECCION", "seccion": self.prim_m.id},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)


class CategoriaTests(APITestCase):
    """`categoria_permitida`: eje funcional, ortogonal al vertical (RF25)."""

    def setUp(self):
        self.prim_m = Seccion.objects.create(nivel=Seccion.Nivel.PRIMARIA, nombre="3A", turno=Seccion.Turno.MANANA)
        self.grupo_tes = GrupoPersonalizado.objects.create(nombre="Cuotas")
        self.grupo_tes.secciones.set([self.prim_m])
        self.grupo_otro = GrupoPersonalizado.objects.create(nombre="Otro")
        self.admin = Usuario.objects.create(username="93000001", dni="93000001", rol=Usuario.Rol.ADMINISTRADOR)
        self.direc = Usuario.objects.create(username="93000002", dni="93000002", rol=Usuario.Rol.AUTORIDAD, cargo=Usuario.Cargo.DIRECTOR)
        self.tesor = Usuario.objects.create(username="93000003", dni="93000003", rol=Usuario.Rol.AUTORIDAD, cargo=Usuario.Cargo.TESORERO)
        self.docen = Usuario.objects.create(username="93000004", dni="93000004", rol=Usuario.Rol.DOCENTE)
        AlcanceGrupo.objects.create(autoridad=self.tesor, grupo=self.grupo_tes)

    def test_tesorero_solo_arancelario(self):
        self.assertTrue(_com(T.ESCUELA, Cat.ARANCELARIO).categoria_permitida(self.tesor))
        self.assertFalse(_com(T.ESCUELA, Cat.ACADEMICO).categoria_permitida(self.tesor))

    def test_director_solo_academico(self):
        self.assertTrue(_com(T.ESCUELA, Cat.ACADEMICO).categoria_permitida(self.direc))
        self.assertFalse(_com(T.ESCUELA, Cat.ARANCELARIO).categoria_permitida(self.direc))

    def test_docente_solo_academico(self):
        self.assertTrue(_com(T.ESCUELA, Cat.ACADEMICO).categoria_permitida(self.docen))
        self.assertFalse(_com(T.ESCUELA, Cat.ARANCELARIO).categoria_permitida(self.docen))

    def test_admin_ambas(self):
        self.assertTrue(_com(T.ESCUELA, Cat.ARANCELARIO).categoria_permitida(self.admin))
        self.assertTrue(_com(T.ESCUELA, Cat.ACADEMICO).categoria_permitida(self.admin))

    def test_ortogonalidad_de_compuertas(self):
        # arancelario a su grupo -> pasa ambas
        c_ok = _com(T.GRUPO, Cat.ARANCELARIO, grupo=self.grupo_tes)
        self.assertTrue(c_ok.destino_en_alcance(self.tesor) and c_ok.categoria_permitida(self.tesor))
        # arancelario a grupo ajeno -> la vertical frena
        c_vert = _com(T.GRUPO, Cat.ARANCELARIO, grupo=self.grupo_otro)
        self.assertTrue(c_vert.categoria_permitida(self.tesor))
        self.assertFalse(c_vert.destino_en_alcance(self.tesor))
        # academico a su grupo -> la funcional frena
        c_func = _com(T.GRUPO, Cat.ACADEMICO, grupo=self.grupo_tes)
        self.assertTrue(c_func.destino_en_alcance(self.tesor))
        self.assertFalse(c_func.categoria_permitida(self.tesor))
