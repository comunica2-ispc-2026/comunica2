from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario del sistema con rol asignado.

    Extiende el usuario estándar de Django (username, email, password,
    first_name, last_name) agregando el rol que define sus permisos
    dentro de Comunica2.
    """

    class Rol(models.TextChoices):
        FAMILIA = "FAMILIA", "Familia"
        DOCENTE = "DOCENTE", "Docente"
        AUTORIDAD = "AUTORIDAD", "Autoridad"
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.FAMILIA,
    )

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"