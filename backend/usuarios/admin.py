from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin del usuario custom: hereda el admin estandar y suma dni + rol + cargo."""
    search_fields = UserAdmin.search_fields + ("dni",)
    list_display = ("username", "dni", "first_name", "last_name", "rol", "cargo", "is_active")
    list_filter = UserAdmin.list_filter + ("rol", "cargo")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("dni", "first_name", "last_name", "email")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
        ("Rol en Comunica2", {"fields": ("rol", "cargo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Información personal", {"fields": ("dni", "first_name", "last_name", "email")}),
        ("Rol en Comunica2", {"fields": ("rol", "cargo")}),
    )