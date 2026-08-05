"""
Permisos de la app `comunicados`.

Dos capas de autorización, separadas a propósito:

1. Por ROL (este archivo): quién puede *intentar* emitir. Desde la S06 emiten
   administrador, autoridad Y docente (RF08); la familia no entra por este
   endpoint (su acceso es la bandeja, filtrada por token).
2. Por OBJETO (en el modelo + la vista, no acá): a *qué* puede emitir cada uno,
   vía `Comunicado.destino_en_alcance` → "destino ⊆ alcance del emisor" (BK26).
   El docente queda acotado a sus secciones y la autoridad a su nivel/turno sin
   que este permiso de rol tenga que saber nada de eso.

El rol abre la puerta; el alcance decide hasta dónde se entra.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from usuarios.models import Usuario


class EmiteAdminAutoridadODocente(BasePermission):
    """Lectura para admin/autoridad/docente; emisión (métodos de escritura) para
    administrador, autoridad o docente. El superusuario pasa por encima
    (comodidad en dev: el superuser de la S02 tiene rol FAMILIA por default).
    El recorte fino de a-qué-puede-emitir lo hace el alcance en la vista.
    """

    ROLES_LECTURA = {
        Usuario.Rol.ADMINISTRADOR,
        Usuario.Rol.AUTORIDAD,
        Usuario.Rol.DOCENTE,
    }
    ROLES_EMISION = {
        Usuario.Rol.ADMINISTRADOR,
        Usuario.Rol.AUTORIDAD,
        Usuario.Rol.DOCENTE,
    }

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return user.rol in self.ROLES_LECTURA
        return user.rol in self.ROLES_EMISION