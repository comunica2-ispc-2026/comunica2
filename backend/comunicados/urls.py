"""
Rutas de la app `comunicados` (fase 1). Router DRF, se incluye bajo `api/` en
`config/urls.py`.

    GET/POST          /api/comunicados/
    GET/PUT/PATCH/DEL /api/comunicados/<id>/
    GET               /api/comunicados/<id>/entregas/   (estado de acuse)

La bandeja del familiar (`mi-bandeja/`) y el acuse llegan en HU-08.
"""

from rest_framework.routers import DefaultRouter

from .views import ComunicadoViewSet

router = DefaultRouter()
router.register("comunicados", ComunicadoViewSet, basename="comunicado")

urlpatterns = router.urls
