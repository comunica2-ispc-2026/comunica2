"""
App `alumnos` — núcleo académico de Comunica2.

Modela lo que la libreta en papel no puede: quiénes son los alumnos y en qué
sección están. Cubre RF05 y RF07 (backlog Alta BK07). El vínculo con las
familias (RF06) llega en HU-05, sobre esta base.

Decisiones que viajan al oficial:
- El alumno NO es un Usuario (no logea). La familia actúa por él. Los 4 roles
  del sistema son administrador/autoridad/docente/familia (RF01); ninguno es
  alumno.
- El campo `dni` reusa el patrón del spike de login: CharField (no Integer, para
  no perder ceros a la izquierda) + RegexValidator. La validación la garantizan
  serializers/forms, no el .save() directo.
"""

from django.core.validators import RegexValidator
from django.db import models

dni_validator = RegexValidator(r"^\d{7,8}$", "El DNI debe tener 7 u 8 dígitos.")


class Seccion(models.Model):
    class Nivel(models.TextChoices):
        INICIAL = "INICIAL", "Inicial"
        PRIMARIA = "PRIMARIA", "Primaria"
        SECUNDARIA = "SECUNDARIA", "Secundaria"

    class Turno(models.TextChoices):
        MANANA = "MANANA", "Mañana"
        TARDE = "TARDE", "Tarde"

    nivel = models.CharField(max_length=12, choices=Nivel.choices, default=Nivel.PRIMARIA)
    nombre = models.CharField(max_length=20, help_text='Ej. "3°A" o "Sala 2"')
    turno = models.CharField(max_length=10, choices=Turno.choices, default=Turno.MANANA)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nivel", "nombre", "turno"]
        constraints = [
            models.UniqueConstraint(
                fields=["nivel", "nombre", "turno"], name="uniq_seccion_nivel_nombre_turno"
            )
        ]

    def __str__(self):
        return f"{self.get_nivel_display()} . {self.nombre} ({self.get_turno_display()})"


class Alumno(models.Model):
    """Entidad central. Campos según RF05 (nombre, apellido, DNI, sección,
    turno, domicilio).

    - `turno` no se guarda acá: se deriva de la sección (`alumno.seccion.turno`),
      así no puede quedar inconsistente con ella.
    - Los familiares (RF06) llegan en HU-05 vía la tabla `Vinculo`; en esta HU el
      alumno existe por sí mismo.
    """

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True, validators=[dni_validator])
    domicilio = models.CharField(max_length=200, blank=True)

    # PROTECT: no se borra una sección que todavía tiene alumnos; hay que
    # reasignarlos primero (decisión intencional). null=True porque un alumno
    # puede existir antes de que el admin lo asigne a una sección (RF07).
    seccion = models.ForeignKey(
        Seccion,
        on_delete=models.PROTECT,
        related_name="alumnos",
        null=True,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["apellido", "nombre"]

    @property
    def turno(self):
        return self.seccion.turno if self.seccion else None

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni})"
