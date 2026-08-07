"""Registro en el admin de la app `institucion`.

Deja cargar a mano las asignaciones de alcance (docente->secciones,
autoridad->nivel/turno, tesorero->grupos) y los Grupos Personalizados desde el
admin en :8001, mismo enfoque de smoke test manual que el resto del proyecto.
"""

from django.contrib import admin

from .models import (
    AlcanceAutoridad,
    AlcanceGrupo,
    AsignacionDocente,
    GrupoPersonalizado,
)


@admin.register(AsignacionDocente)
class AsignacionDocenteAdmin(admin.ModelAdmin):
    list_display = ["docente", "seccion", "activa"]
    list_filter = ["activa", "seccion"]
    search_fields = ["docente__username", "docente__dni"]
    autocomplete_fields = ["docente", "seccion"]


@admin.register(AlcanceAutoridad)
class AlcanceAutoridadAdmin(admin.ModelAdmin):
    list_display = ["autoridad", "nivel", "turno"]
    list_filter = ["nivel", "turno"]
    search_fields = ["autoridad__username", "autoridad__dni"]
    autocomplete_fields = ["autoridad"]


@admin.register(GrupoPersonalizado)
class GrupoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]
    filter_horizontal = ["secciones"]


@admin.register(AlcanceGrupo)
class AlcanceGrupoAdmin(admin.ModelAdmin):
    list_display = ["autoridad", "grupo"]
    list_filter = ["grupo"]
    search_fields = ["autoridad__username", "autoridad__dni", "grupo__nombre"]
    autocomplete_fields = ["autoridad", "grupo"]