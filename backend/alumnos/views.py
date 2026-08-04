"""Vistas del bloque alumnos — HU-04 (RF05, RF07).

Un endpoint:
- alumnos/     CRUD de alumnos, con filtro ?seccion=<id>.

Escritura: solo administrador (ver permissions.SoloAdminEscribe). Lectura:
admin/autoridad/docente. La vista de la familia (`mis-alumnos`) y el ABM de
secciones llegan en HU-05 y HU-06 respectivamente.
"""

from rest_framework import viewsets

from config.mixins import BajaLogicaMixin

from .models import Alumno
from .permissions import SoloAdminEscribe
from .serializers import AlumnoSerializer


class AlumnoViewSet(BajaLogicaMixin, viewsets.ModelViewSet):
    serializer_class = AlumnoSerializer
    permission_classes = [SoloAdminEscribe]
    soft_delete_field = "activo"

    def get_queryset(self):
        qs = Alumno.objects.select_related("seccion").all()
        seccion = self.request.query_params.get("seccion")
        if seccion:
            qs = qs.filter(seccion_id=seccion)
        return qs
