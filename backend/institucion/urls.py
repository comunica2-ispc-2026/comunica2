"""Rutas de `institucion`. Router DRF, se incluye bajo `api/` en `config/urls.py`.

    /api/asignaciones-docente/   AsignacionDocente (docente <-> seccion)
    /api/alcances-autoridad/     AlcanceAutoridad  (autoridad -> nivel/turno)
    /api/grupos/                 GrupoPersonalizado (grupos de secciones)
    /api/alcances-grupo/         AlcanceGrupo      (autoridad/tesorero -> grupo)
"""

from rest_framework.routers import DefaultRouter

from .views import (
    AlcanceAutoridadViewSet,
    AlcanceGrupoViewSet,
    AsignacionDocenteViewSet,
    GrupoPersonalizadoViewSet,
)

router = DefaultRouter()
router.register("asignaciones-docente", AsignacionDocenteViewSet, basename="asignacion-docente")
router.register("alcances-autoridad", AlcanceAutoridadViewSet, basename="alcance-autoridad")
router.register("grupos", GrupoPersonalizadoViewSet, basename="grupo")
router.register("alcances-grupo", AlcanceGrupoViewSet, basename="alcance-grupo")

urlpatterns = router.urls
