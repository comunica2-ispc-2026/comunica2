"""
Helpers de vista a nivel proyecto (no atados a una app).

`BajaLogicaMixin` unifica el criterio de borrado, extendiendo la decision que ya
se tomo para Usuario al resto de los modelos que fueron disenados con flag de
baja logica (`activo`/`activa`) + FKs `PROTECT`:

- Si el ViewSet declara `soft_delete_field`, el DELETE apaga ese flag en vez de
  borrar la fila. No se pierde historial y, de paso, no choca con los PROTECT.
- Si no lo declara, intenta el borrado real y traduce un `ProtectedError` a un
  409 limpio, en vez del 500 crudo que devuelve DRF por defecto cuando una FK
  PROTECT bloquea el delete.

Se pone en `config/` (paquete del proyecto, ya en el path) para no crear una app
nueva ni tocar INSTALLED_APPS por un solo mixin. Si mas adelante crece la caja de
utilidades compartidas, es candidata a mudarse a un app `core`/`common` propio.
"""

from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response


class BajaLogicaMixin:
    #: nombre del campo booleano de baja logica (p.ej. "activo" / "activa").
    #: Si es None, el DELETE es borrado real (con red de seguridad ante PROTECT).
    soft_delete_field = None

    def perform_destroy(self, instance):
        field = self.soft_delete_field
        if field:
            setattr(instance, field, False)
            instance.save(update_fields=[field])
        else:
            instance.delete()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "No se puede eliminar: hay registros que dependen de este objeto."},
                status=status.HTTP_409_CONFLICT,
            )
