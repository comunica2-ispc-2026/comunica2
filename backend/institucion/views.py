"""Vistas de `institucion` — administracion del alcance (admin-only).

Cuatro ViewSets CRUD, todos con permiso SoloAdmin. Son la contracara por API del
admin de Django que hoy carga estas tablas a mano: es lo que le permite al
administrador manejar el resolver de alcance sin salir de la app.

    GET/POST/PUT/PATCH/DELETE  /api/asignaciones-docente/
    GET/POST/PUT/PATCH/DELETE  /api/alcances-autoridad/
    GET/POST/PUT/PATCH/DELETE  /api/grupos/
    GET/POST/PUT/PATCH/DELETE  /api/alcances-grupo/
"""

from rest_framework import viewsets

from config.mixins import BajaLogicaMixin

from .models import (
    AlcanceAutoridad,
    AlcanceGrupo,
    AsignacionDocente,
    GrupoPersonalizado,
)
from .permissions import SoloAdmin
from .serializers import (
    AlcanceAutoridadSerializer,
    AlcanceGrupoSerializer,
    AsignacionDocenteSerializer,
    GrupoPersonalizadoSerializer,
)


class AsignacionDocenteViewSet(BajaLogicaMixin, viewsets.ModelViewSet):
    queryset = AsignacionDocente.objects.select_related("docente", "seccion").all()
    serializer_class = AsignacionDocenteSerializer
    permission_classes = [SoloAdmin]
    soft_delete_field = "activa"


class AlcanceAutoridadViewSet(viewsets.ModelViewSet):
    queryset = AlcanceAutoridad.objects.select_related("autoridad").all()
    serializer_class = AlcanceAutoridadSerializer
    permission_classes = [SoloAdmin]


class GrupoPersonalizadoViewSet(BajaLogicaMixin, viewsets.ModelViewSet):
    queryset = GrupoPersonalizado.objects.prefetch_related("secciones").all()
    serializer_class = GrupoPersonalizadoSerializer
    permission_classes = [SoloAdmin]
    soft_delete_field = "activo"


class AlcanceGrupoViewSet(viewsets.ModelViewSet):
    queryset = AlcanceGrupo.objects.select_related("autoridad", "grupo").all()
    serializer_class = AlcanceGrupoSerializer
    permission_classes = [SoloAdmin]
