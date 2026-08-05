"""
Rutas de la app `comunicados` (fase 1). Router DRF, se incluye bajo `api/` en
`config/urls.py`.

    GET/POST          /api/comunicados/
    GET/PUT/PATCH/DEL /api/comunicados/<id>/
    GET               /api/comunicados/<id>/entregas/   (estado de acuse)
    GET               /api/mi-bandeja/                  (bandeja del familiar)
    GET               /api/mi-bandeja/<id>/
    POST              /api/mi-bandeja/<id>/acusar/      (RF09/RF10)
"""

from rest_framework.routers import DefaultRouter

from .views import ComunicadoViewSet, MiBandejaViewSet

router = DefaultRouter()
router.register("comunicados", ComunicadoViewSet, basename="comunicado")
router.register("mi-bandeja", MiBandejaViewSet, basename="mi-bandeja")

urlpatterns = router.urls
