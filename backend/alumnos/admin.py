"""Registro en el admin de la app `alumnos`.

Pensado para el smoke test manual (mismo enfoque que la Sesión 02): dar de alta
secciones, alumnos y vínculos desde el admin en :8001 antes de tener la API.
El `VinculoInline` deja cargar los familiares de un alumno en la misma pantalla.
"""

from django.contrib import admin

from .models import Alumno, Seccion, Vinculo


class VinculoInline(admin.TabularInline):
    model = Vinculo
    extra = 1
    autocomplete_fields = ["usuario"]


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ["nombre", "turno", "activa"]
    list_filter = ["turno", "activa"]
    search_fields = ["nombre"]


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ["apellido", "nombre", "dni", "seccion", "activo"]
    list_filter = ["seccion", "activo"]
    search_fields = ["apellido", "nombre", "dni"]
    inlines = [VinculoInline]


@admin.register(Vinculo)
class VinculoAdmin(admin.ModelAdmin):
    list_display = ["usuario", "alumno", "parentesco", "activo"]
    list_filter = ["parentesco", "activo"]
    search_fields = ["usuario__username", "usuario__dni", "alumno__apellido", "alumno__dni"]
    autocomplete_fields = ["usuario", "alumno"]