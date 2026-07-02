from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin del usuario custom: hereda el admin estándar y suma el rol."""

    list_display = ("username", "email", "first_name", "last_name", "rol", "is_active")
    list_filter = UserAdmin.list_filter + ("rol",)
    fieldsets = UserAdmin.fieldsets + (
        ("Rol en Comunica2", {"fields": ("rol",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rol en Comunica2", {"fields": ("rol",)}),
    )