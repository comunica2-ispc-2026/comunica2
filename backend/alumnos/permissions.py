"""Permisos del bloque alumnos — fase 1 (por ROL, sin scoping por objeto).

Reparto acordado:
- administrador -> lee y escribe. Es el único que escribe: admin es el
  superconjunto real de autoridad, no un empate con un escalón.
- autoridad / docente -> solo lectura. (Lo que distingue a la autoridad no es
  escribir alumnos, es emitir circulares: eso vive en el bloque de comunicados.)
- familia -> no entra por estos endpoints; usa `mis-alumnos`.

Lo que NO hace esta fase: acotar la lectura del docente a sus secciones o la de
la autoridad a su nivel. Eso es permiso a nivel de objeto y es una etapa propia,
que se apoyará en las asignaciones Docente<->Sección y Autoridad<->Nivel (todavía
no modeladas). Estructura y autorización van separadas a propósito.

El superusuario de Django pasa por encima de todo (cómodo para el smoke test:
el superuser de la Sesión 02 tiene rol FAMILIA por default, así que sin este
bypass no podría escribir).
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS

from usuarios.models import Usuario

ROLES_LECTURA = {
    Usuario.Rol.ADMINISTRADOR,
    Usuario.Rol.AUTORIDAD,
    Usuario.Rol.DOCENTE,
}


class SoloAdminEscribe(BasePermission):
    message = "Solo el administrador puede modificar estos datos."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return user.rol in ROLES_LECTURA
        return user.rol == Usuario.Rol.ADMINISTRADOR