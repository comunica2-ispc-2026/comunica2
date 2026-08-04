"""Registro en el admin de la app `alumnos` — HU-04 (Seccion + Alumno).

Pensado para el smoke test manual (mismo enfoque que la Sesión 02): dar de alta
secciones y alumnos desde el admin antes de tener toda la API. El registro de
`Vinculo` (y su inline en el alumno) llega en HU-05.
"""

from django.contrib import admin

from .models import Alumno, Seccion


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ["nombre", "nivel", "turno", "activa"]
    list_filter = ["nivel", "turno", "activa"]
    search_fields = ["nombre"]


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ["apellido", "nombre", "dni", "seccion", "activo"]
    list_filter = ["seccion", "activo"]
    search_fields = ["apellido", "nombre", "dni"]
