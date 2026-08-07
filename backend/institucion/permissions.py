"""Permiso de la app `institucion` — administracion del alcance.

Admin-only para todo (mismo criterio que usuarios.SoloAdmin): quien puede
asignar docentes a secciones, fijar el alcance de una autoridad o armar Grupos
Personalizados es solo el administrador. El resto de los roles no toca la
estructura de alcance; la consume (via el resolver), no la edita.

Superuser bypass, igual que el resto de la casa.
"""

from rest_framework.permissions import BasePermission

from usuarios.models import Usuario


class SoloAdmin(BasePermission):
    message = "Solo el administrador puede administrar el alcance."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser:
            return True
        return user.rol == Usuario.Rol.ADMINISTRADOR
