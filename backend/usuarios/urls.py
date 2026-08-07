"""Ruteo de `usuarios` — HU-01 (login/logout) + HU-02 (perfil y contraseña propia).

Se incluye bajo `api/` en `config/urls.py`.

    POST         /api/auth/login/
    POST         /api/auth/logout/
    GET/PATCH    /api/auth/me/                 (perfil propio)
    POST         /api/auth/cambiar-password/   (cambio de la propia contraseña)

El CRUD de usuarios (ABM, admin-only) llega con HU-03.
"""

from django.urls import path

from .views import CambiarPasswordView, LoginDNIView, LogoutView, PerfilView

urlpatterns = [
    path("auth/login/", LoginDNIView.as_view(), name="login-dni"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", PerfilView.as_view(), name="perfil"),
    path("auth/cambiar-password/", CambiarPasswordView.as_view(), name="cambiar-password"),
]
