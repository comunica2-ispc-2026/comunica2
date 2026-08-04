"""Tests de HU-01 — inicio de sesión con control de acceso por rol.

`APITestCase` corre sobre una DB de test aislada y transaccional: cada test se
ejecuta en su propia transacción y se revierte al terminar, así que no hace falta
sembrar con prefijo ni limpiar (a diferencia del runner in-process del lab).

Cubre:
- Login por DNI: credenciales correctas -> 200 + token + rol; password errónea,
  DNI inexistente y usuario inactivo -> 400 (mismo mensaje: no se filtra qué falló).
- API cerrada por defecto: logout sin token -> 401.
- El token autentica y queda invalidado tras el logout.
"""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Usuario

CLAVE = "clave-secreta-123"


class LoginDNITests(APITestCase):
    def setUp(self):
        self.docente = Usuario.objects.create(
            username="30111222", dni="30111222", rol=Usuario.Rol.DOCENTE
        )
        self.docente.set_password(CLAVE)
        self.docente.save()

    def test_login_correcto_devuelve_token_y_rol(self):
        r = self.client.post(
            "/api/auth/login/",
            {"dni": "30111222", "password": CLAVE},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("token", r.json())
        self.assertEqual(r.json()["rol"], Usuario.Rol.DOCENTE)

    def test_login_password_incorrecta(self):
        r = self.client.post(
            "/api/auth/login/",
            {"dni": "30111222", "password": "clave-equivocada-000"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_dni_inexistente(self):
        r = self.client.post(
            "/api/auth/login/",
            {"dni": "99999999", "password": CLAVE},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_usuario_inactivo_no_entra(self):
        self.docente.is_active = False
        self.docente.save(update_fields=["is_active"])
        r = self.client.post(
            "/api/auth/login/",
            {"dni": "30111222", "password": CLAVE},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create(
            username="30111333", dni="30111333", rol=Usuario.Rol.FAMILIA
        )
        self.user.set_password(CLAVE)
        self.user.save()

    def test_logout_sin_token_401(self):
        # API cerrada por defecto: sin credenciales no se entra.
        r = self.client.post("/api/auth/logout/")
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalida_el_token(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        r = self.client.post("/api/auth/logout/")
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        # El token ya no existe: reintentar con la misma credencial -> 401.
        r2 = self.client.post("/api/auth/logout/")
        self.assertEqual(r2.status_code, status.HTTP_401_UNAUTHORIZED)
