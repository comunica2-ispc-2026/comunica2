"""Ruteo del bloque alumnos — HU-04. Se incluye bajo api/ en config/urls.py.

`AlumnoViewSet` define get_queryset dinámico (sin atributo `queryset`), así que el
router necesita `basename` explícito.

    GET/POST          /api/alumnos/          (?seccion=<id> para filtrar)
    GET/PUT/PATCH/DEL /api/alumnos/<id>/     (DELETE = baja lógica)

secciones/, vinculos/ y mis-alumnos/ se registran en HU-06 y HU-05.
"""

from rest_framework.routers import DefaultRouter

from .views import AlumnoViewSet

router = DefaultRouter()
router.register("alumnos", AlumnoViewSet, basename="alumno")

urlpatterns = router.urls
