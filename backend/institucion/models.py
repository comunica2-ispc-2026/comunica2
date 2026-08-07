"""
App `institucion` — alcance por objeto (scoping) de Comunica2.

Es la pieza de mayor palanca de la fase 2: quién puede comunicarse con quién,
según su rol y su asignación real dentro de la escuela. Cubre RF22 (alcance de
autoridad), RF23 (secciones de un docente) y RF26 (Grupos Personalizados); es la
base del row-level auth (BK26).

Idea de fondo (lo que viaja al oficial):
- La estructura de alcance vive SEPARADA de la autorización. Estas tablas dicen
  "qué toca cada usuario"; el "puede o no puede" se resuelve aparte, reduciendo
  todo a un set concreto de secciones/alumnos (ver `alcance.py`).
- La regla de dominio "un AsignacionDocente apunta a un usuario con rol DOCENTE"
  y "un AlcanceAutoridad/AlcanceGrupo a un usuario con rol AUTORIDAD" se deja
  PERMISIVA en el modelo y se aplica en el serializer (igual que en Vinculo).

Eje vertical del alcance de autoridad, en DOS fuentes (unificadas en alcance.py):
- `AlcanceAutoridad` (nivel/turno): director/vicedirector (turno NULL = nivel
  completo) y preceptor (turno seteado).
- `AlcanceGrupo` (grupos): el tesorero, cuyo alcance son Grupos Personalizados
  que cruzan turnos y niveles.

Diferido a un slice posterior (se diseña, no se construye — "ninguna tabla nace
muerta"):
- El `cargo` de la autoridad (director/vice/preceptor/tesorero) y las categorías
  de comunicado por cargo (eje FUNCIONAL, RF25). Vive en comunicados, no acá.
"""

from django.conf import settings
from django.db import models

from alumnos.models import Seccion


class AsignacionDocente(models.Model):
    """RF23: el administrador asigna a un docente una o más secciones como
    alcance de su gestión. `activa` permite desasignar sin perder el registro.
    """

    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="secciones_asignadas",
    )
    seccion = models.ForeignKey(
        Seccion,
        on_delete=models.CASCADE,
        related_name="docentes_asignados",
    )
    activa = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["docente", "seccion"], name="uniq_asignacion_docente_seccion"
            )
        ]

    def __str__(self):
        return f"{self.docente} -> {self.seccion}"


class AlcanceAutoridad(models.Model):
    """RF22: alcance VERTICAL de una autoridad por nivel/turno.

    - `turno` NULL  -> el nivel completo, ambos turnos (director/vicedirector).
    - `turno` seteado -> acota a ese nivel-turno (preceptor).

    El tesorero NO usa esta tabla: su alcance va por AlcanceGrupo.
    """

    autoridad = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alcances",
    )
    nivel = models.CharField(max_length=12, choices=Seccion.Nivel.choices)
    turno = models.CharField(
        max_length=10, choices=Seccion.Turno.choices, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["autoridad", "nivel", "turno"],
                name="uniq_alcance_autoridad_nivel_turno",
            )
        ]

    def __str__(self):
        alcance = self.get_nivel_display()
        if self.turno:
            alcance += f" ({self.get_turno_display()})"
        return f"{self.autoridad} -> {alcance}"


class GrupoPersonalizado(models.Model):
    """RF26: agrupacion libre de secciones definida por el administrador segun el
    criterio de la institucion (ej. un ciclo de facturacion como "Primaria 1 a
    3"). Puede cruzar niveles y turnos: rompe a proposito el arbol
    Nivel->Turno->Seccion. Es la base del alcance del tesorero (RF25).
    """

    nombre = models.CharField(max_length=80, unique=True)
    secciones = models.ManyToManyField(Seccion, related_name="grupos", blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class AlcanceGrupo(models.Model):
    """RF22 (tesorero): alcance de una autoridad por Grupos Personalizados.

    Tabla APARTE de AlcanceAutoridad a proposito: el alcance del tesorero es un
    scope de otro tipo (grupos que cruzan turnos), no un nivel/turno. Meterlo como
    un `grupo` nullable dentro de AlcanceAutoridad daria una fila polimorfica
    turbia. `secciones_en_alcance` unifica ambas fuentes en un solo set -- que es
    el modelo honesto de "scopes de tipos distintos".
    """

    autoridad = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alcances_grupo",
    )
    grupo = models.ForeignKey(
        GrupoPersonalizado,
        on_delete=models.CASCADE,
        related_name="alcances",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["autoridad", "grupo"], name="uniq_alcance_grupo"
            )
        ]

    def __str__(self):
        return f"{self.autoridad} -> grupo {self.grupo}"