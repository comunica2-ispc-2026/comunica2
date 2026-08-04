"""Ruteo de `usuarios` — HU-01: login/logout por DNI.

Se incluye bajo `api/` en `config/urls.py`.

    POST  /api/auth/login/
    POST  /api/auth/logout/

El CRUD de usuarios (ABM, admin-only) llega con HU-03; el perfil propio y el
cambio de contraseña, con HU-02.
"""

from django.urls import path

from .views import LoginDNIView, LogoutView

urlpatterns = [
    path("auth/login/", LoginDNIView.as_view(), name="login-dni"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]
