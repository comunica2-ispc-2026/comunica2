"""Ruteo del bloque alumnos. Se incluye bajo api/ en config/urls.py.

AlumnoViewSet y MisAlumnosViewSet definen get_queryset dinámico (sin atributo
`queryset`), así que el router necesita `basename` explícito para esos dos.

    /api/alumnos/        CRUD de alumnos (?seccion=<id>)
    /api/vinculos/       CRUD del vínculo familia<->alumno
    /api/mis-alumnos/    read-only: los hijos de la familia logueada

secciones/ se registra en HU-06 (ABM de secciones).
"""

from rest_framework.routers import DefaultRouter

from .views import AlumnoViewSet, MisAlumnosViewSet, VinculoViewSet

router = DefaultRouter()
router.register("alumnos", AlumnoViewSet, basename="alumno")
router.register("vinculos", VinculoViewSet)
router.register("mis-alumnos", MisAlumnosViewSet, basename="mis-alumno")

urlpatterns = router.urls
