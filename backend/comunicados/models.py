"""
App `comunicados` -- circulares y acuse de recibo de Comunica2.

Cubre RF08 (emitir comunicados) y RF09/RF10 (acuse de recibo con fecha/hora).
Backlog BK08/BK09, y desde la S06 el row-level auth de la escritura (BK26).

Diseno fase-1 (espeja el corte fase-1/fase-2 de `alumnos`):
- Bandeja por ENTREGA MATERIALIZADA (fan-out on write): al emitir, una fila de
  entrega por cada familiar vinculado a cada alumno del alcance. La bandeja es un
  SELECT directo; "quien acuso / quien no" es una agregacion sobre esa tabla.
- Grano de la entrega = (comunicado, familiar, alumno): un familiar con varios
  hijos recibe y acusa por CADA hijo.
- Emision por ROL (admin/autoridad/docente) -> vive en permissions.py.

Ampliacion fase-2 (S06 + 7a) -- emision acotada / scoping por objeto:
- `tipo_destino`: INDIVIDUAL|SECCION|TURNO|NIVEL|GRUPO|ESCUELA, con un campo
  localizador por tipo (alumno / seccion / nivel+turno / nivel / grupo / --).
- `destino_en_alcance(user)` conecta el resolver de `institucion`: valida
  "destino subset del alcance del emisor" (BK26). El admin es el unico con
  alcance total y el unico que llega a ESCUELA (doc 3.2: ninguna autoridad
  abarca toda la institucion).

Eje funcional (7b): `categoria` (ACADEMICO/ARANCELARIO) + `categoria_permitida(user)`
segun el `cargo` de la autoridad (RF25: tesorero solo arancelarios). Es la SEGUNDA
compuerta de la emision, ortogonal al alcance vertical (destino_en_alcance).

Diferido a un slice posterior (se disena, no se construye):
- `leido_en` (abrio != acuso): se agrega si el requerimiento lo pide.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from alumnos.models import Alumno, Seccion, Vinculo
from usuarios.models import Usuario

# Campos localizadores posibles. Por cada tipo de destino (REQUERIDOS_POR_TIPO),
# cuales deben venir seteados; el resto debe quedar nulo. Regla de coherencia
# unica, consumida por clean() y por el serializer.
_LOCALIZADORES = ("alumno", "seccion", "nivel", "turno", "grupo")


class Comunicado(models.Model):
    class TipoDestino(models.TextChoices):
        INDIVIDUAL = "INDIVIDUAL", "Un alumno"
        SECCION = "SECCION", "Una seccion"
        TURNO = "TURNO", "Un nivel-turno"
        NIVEL = "NIVEL", "Un nivel completo"
        GRUPO = "GRUPO", "Un grupo personalizado"
        ESCUELA = "ESCUELA", "Toda la escuela"

    REQUERIDOS_POR_TIPO = {
        TipoDestino.INDIVIDUAL: {"alumno"},
        TipoDestino.SECCION: {"seccion"},
        TipoDestino.TURNO: {"nivel", "turno"},
        TipoDestino.NIVEL: {"nivel"},
        TipoDestino.GRUPO: {"grupo"},
        TipoDestino.ESCUELA: set(),
    }

    class Categoria(models.TextChoices):
        ACADEMICO = "ACADEMICO", "Academico"
        ARANCELARIO = "ARANCELARIO", "Arancelario"

    emisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="comunicados_emitidos",
    )
    titulo = models.CharField(max_length=150)
    cuerpo = models.TextField()

    tipo_destino = models.CharField(
        max_length=10, choices=TipoDestino.choices, default=TipoDestino.SECCION
    )

    # Localizadores. Cual va seteado depende de tipo_destino; la coherencia la
    # garantiza clean(). Todos nullables (ESCUELA no lleva ninguno). PROTECT en
    # las FK: no se borra un alumno/seccion/grupo con comunicados dirigidos.
    alumno = models.ForeignKey(
        "alumnos.Alumno", on_delete=models.PROTECT,
        related_name="comunicados_individuales", null=True, blank=True,
    )
    seccion = models.ForeignKey(
        "alumnos.Seccion", on_delete=models.PROTECT,
        related_name="comunicados", null=True, blank=True,
    )
    nivel = models.CharField(
        max_length=12, choices=Seccion.Nivel.choices, null=True, blank=True
    )
    turno = models.CharField(
        max_length=10, choices=Seccion.Turno.choices, null=True, blank=True
    )
    grupo = models.ForeignKey(
        "institucion.GrupoPersonalizado", on_delete=models.PROTECT,
        related_name="comunicados", null=True, blank=True,
    )

    # Eje funcional (7b): que TIPO de comunicado es, no a quien va. La regla de
    # quien puede emitir cada categoria vive en categoria_permitida (RF25).
    categoria = models.CharField(
        max_length=12, choices=Categoria.choices, default=Categoria.ACADEMICO
    )

    requiere_acuse = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.titulo} -> {self.descripcion_destino()}"

    # --- coherencia tipo <-> localizadores -----------------------------------

    @classmethod
    def errores_coherencia(cls, tipo, *, alumno, seccion, nivel, turno, grupo):
        """Dict {campo: mensaje} con las incoherencias tipo<->localizadores.
        Vacio = coherente. Estatico a proposito: lo usan el modelo (clean) y el
        serializer, sin duplicar la regla. Los valores son 'presente o no'."""
        try:
            requeridos = cls.REQUERIDOS_POR_TIPO[tipo]
        except KeyError:
            return {"tipo_destino": "Tipo de destino desconocido."}
        presentes = {
            "alumno": alumno, "seccion": seccion, "nivel": nivel,
            "turno": turno, "grupo": grupo,
        }
        display = cls.TipoDestino(tipo).label
        errores = {}
        for campo in _LOCALIZADORES:
            valor = presentes[campo] or None
            if campo in requeridos and not valor:
                errores[campo] = f"Requerido para un comunicado de tipo '{display}'."
            elif campo not in requeridos and valor:
                errores[campo] = f"No corresponde para un comunicado de tipo '{display}'."
        return errores

    def clean(self):
        """La API la ejerce (400 via serializer); el .save() directo no corre
        validators (mismo criterio que el dni en alumnos)."""
        errores = self.errores_coherencia(
            self.tipo_destino,
            alumno=self.alumno_id, seccion=self.seccion_id,
            nivel=self.nivel, turno=self.turno, grupo=self.grupo_id,
        )
        if errores:
            raise ValidationError(errores)

    # --- destino -> secciones / alumnos --------------------------------------

    def _secciones_de_destino(self):
        """Secciones activas que abarca el destino, para SECCION/TURNO/NIVEL/GRUPO.
        Vacio para INDIVIDUAL/ESCUELA, que resuelven sus alumnos por otra via."""
        T = self.TipoDestino
        if self.tipo_destino == T.SECCION:
            return Seccion.objects.filter(pk=self.seccion_id, activa=True)
        if self.tipo_destino == T.TURNO:
            return Seccion.objects.filter(nivel=self.nivel, turno=self.turno, activa=True)
        if self.tipo_destino == T.NIVEL:
            return Seccion.objects.filter(nivel=self.nivel, activa=True)
        if self.tipo_destino == T.GRUPO:
            return Seccion.objects.filter(grupos=self.grupo_id, activa=True)
        return Seccion.objects.none()

    def descripcion_destino(self):
        T = self.TipoDestino
        if self.tipo_destino == T.INDIVIDUAL:
            return str(self.alumno) if self.alumno_id else "un alumno"
        if self.tipo_destino == T.SECCION:
            return str(self.seccion) if self.seccion_id else "una seccion"
        if self.tipo_destino == T.TURNO:
            return f"{self.get_nivel_display()} ({self.get_turno_display()})"
        if self.tipo_destino == T.NIVEL:
            return self.get_nivel_display() or "un nivel"
        if self.tipo_destino == T.GRUPO:
            return f"grupo {self.grupo}" if self.grupo_id else "un grupo"
        return "toda la escuela"

    def alumnos_destinatarios(self):
        """Alumnos activos alcanzados segun tipo_destino. ESCUELA incluye a los
        que aun no tienen seccion asignada (siguen siendo de la escuela); ningun
        otro tipo los alcanza (ver destino_en_alcance)."""
        T = self.TipoDestino
        qs = Alumno.objects.filter(activo=True)
        if self.tipo_destino == T.INDIVIDUAL:
            return qs.filter(pk=self.alumno_id)
        if self.tipo_destino == T.ESCUELA:
            return qs
        return qs.filter(seccion__in=self._secciones_de_destino())

    # --- row-level auth de la escritura (BK26) -------------------------------

    def destino_en_alcance(self, user):
        """True si el destino subset del alcance de `user`. Validacion de emision
        de fase 2. Reusa el resolver de `institucion` (import diferido para no
        tocar get_user_model durante la carga de apps).

        - admin/superuser: alcance total -> siempre True (unico que llega a
          ESCUELA; doc 3.2: ninguna autoridad abarca toda la escuela).
        - INDIVIDUAL: el alumno debe caer en alumnos_en_alcance(user).
        - SECCION/TURNO/NIVEL/GRUPO: todas las secciones del destino subset de
          secciones_en_alcance(user). Un destino vacio (ej. nivel/grupo sin
          secciones) no se emite a ciegas -> False.
        """
        from institucion.alcance import alumnos_en_alcance, secciones_en_alcance

        if user.is_superuser or user.rol == Usuario.Rol.ADMINISTRADOR:
            return True
        if self.tipo_destino == self.TipoDestino.ESCUELA:
            return False
        if self.tipo_destino == self.TipoDestino.INDIVIDUAL:
            return alumnos_en_alcance(user).filter(pk=self.alumno_id).exists()

        destino = self._secciones_de_destino()
        if not destino.exists():
            return False
        return not destino.exclude(pk__in=secciones_en_alcance(user)).exists()

    def categoria_permitida(self, user):
        """True si `user` puede emitir un comunicado de ESTA categoria (RF25),
        el eje FUNCIONAL -- ortogonal al vertical (destino_en_alcance):

        - admin/superuser: cualquier categoria.
        - tesorero (autoridad con cargo TESORERO): solo ARANCELARIO.
        - el resto (director/vice/preceptor/docente): solo ACADEMICO.
        """
        if user.is_superuser or user.rol == Usuario.Rol.ADMINISTRADOR:
            return True
        es_tesorero = (
            user.rol == Usuario.Rol.AUTORIDAD
            and user.cargo == Usuario.Cargo.TESORERO
        )
        if es_tesorero:
            return self.categoria == self.Categoria.ARANCELARIO
        return self.categoria == self.Categoria.ACADEMICO

    # --- fan-out on write -----------------------------------------------------

    def generar_entregas(self):
        """Fan-out on write: una entrega por cada Vinculo activo a cada alumno
        del alcance. Idempotente (`ignore_conflicts` sobre el unique)."""
        vinculos = Vinculo.objects.filter(
            alumno__in=self.alumnos_destinatarios(), activo=True
        ).select_related("usuario", "alumno")
        entregas = [
            EntregaComunicado(comunicado=self, familiar=v.usuario, alumno=v.alumno)
            for v in vinculos
        ]
        return EntregaComunicado.objects.bulk_create(entregas, ignore_conflicts=True)


class EntregaComunicado(models.Model):
    """Una fila por (comunicado, familiar, alumno). Es la bandeja y el acuse a la
    vez: que exista = fue entregado (RF08); `acusado_en` no nulo = acusado, con
    su fecha/hora (RF09/RF10)."""

    comunicado = models.ForeignKey(
        Comunicado, on_delete=models.CASCADE, related_name="entregas"
    )
    familiar = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entregas_recibidas",
    )
    alumno = models.ForeignKey(
        Alumno, on_delete=models.CASCADE, related_name="entregas"
    )

    entregado_en = models.DateTimeField(auto_now_add=True)
    acusado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-entregado_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["comunicado", "familiar", "alumno"],
                name="uniq_entrega_comunicado_familiar_alumno",
            )
        ]

    @property
    def acusado(self):
        return self.acusado_en is not None

    def __str__(self):
        estado = "acusado" if self.acusado else "pendiente"
        return f"{self.comunicado.titulo} - {self.familiar} / {self.alumno} ({estado})"