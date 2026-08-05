"""Vistas del bloque alumnos (RF05, RF06, RF07).

Tras HU-05, tres endpoints:
- alumnos/     CRUD de alumnos, con filtro ?seccion=<id>.
- vinculos/    CRUD de la relación familia<->alumno.
- mis-alumnos/ read-only; la familia ve SOLO sus hijos, filtrados por el token.

Escritura: solo administrador (ver permissions.SoloAdminEscribe).
Lectura general (alumnos/vinculos): admin/autoridad/docente.
El ABM de secciones (SeccionViewSet) llega en HU-06.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from config.mixins import BajaLogicaMixin

from .models import Alumno, Vinculo
from .permissions import SoloAdminEscribe
from .serializers import AlumnoSerializer, VinculoSerializer


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


class VinculoViewSet(BajaLogicaMixin, viewsets.ModelViewSet):
    queryset = Vinculo.objects.select_related("usuario", "alumno").all()
    serializer_class = VinculoSerializer
    permission_classes = [SoloAdminEscribe]
    soft_delete_field = "activo"


class MisAlumnosViewSet(viewsets.ReadOnlyModelViewSet):
    """La familia logueada ve solo sus hijos vinculados.

    El filtro sale de request.user (el usuario del token), NUNCA de un parámetro
    de la URL: si fuera ?familia=<id>, cualquiera cambiaría el id y espiaría a
    los hijos ajenos. La identidad sale de algo que el cliente no puede falsificar.
    """

    serializer_class = AlumnoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Alumno.objects.filter(
                vinculos__usuario=self.request.user, vinculos__activo=True
            )
            .select_related("seccion")
            .distinct()
        )
