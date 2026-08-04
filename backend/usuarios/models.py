from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class Usuario(AbstractUser):
    """Usuario del sistema con rol asignado.

    Extiende el usuario estándar de Django (username, email, password,
    first_name, last_name) agregando el rol que define sus permisos
    dentro de Comunica2, y —para las autoridades— el cargo, que define el
    eje FUNCIONAL del alcance (qué categoría de comunicado puede emitir).
    """

    class Rol(models.TextChoices):
        FAMILIA = "FAMILIA", "Familia"
        DOCENTE = "DOCENTE", "Docente"
        AUTORIDAD = "AUTORIDAD", "Autoridad"
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"

    class Cargo(models.TextChoices):
        DIRECTOR = "DIRECTOR", "Director/a"
        VICEDIRECTOR = "VICEDIRECTOR", "Vicedirector/a"
        PRECEPTOR = "PRECEPTOR", "Preceptor/a"
        TESORERO = "TESORERO", "Tesorero/a"

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.FAMILIA,
    )

    # Sub-etiqueta del rol, con sentido solo cuando rol=AUTORIDAD. Nullable: los
    # demás roles no llevan cargo. La regla "cargo solo en autoridades" se deja
    # permisiva en el modelo (mismo criterio que el resto); la ejerce el
    # serializer de Usuario si algún día hace falta.
    cargo = models.CharField(
        max_length=20,
        choices=Cargo.choices,
        null=True,
        blank=True,
        help_text="Solo para autoridades. Define qué categoría de comunicado puede emitir.",
    )

    dni = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(r"^\d{7,8}$", "El DNI debe tener 7 u 8 dígitos, sin puntos.")],
        help_text="7 u 8 dígitos, sin puntos ni espacios.",
    )

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"