"""Tests de usuarios — HU-01 (login/logout) + HU-02 (perfil y contraseña propia).

`APITestCase` sobre DB de test aislada.
"""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from .models import Usuario

CLAVE = "clave-secreta-123"


def _cliente(user):
    c = APIClient()
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        c.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return c


class LoginDNITests(APITestCase):
    def setUp(self):
        self.docente = Usuario.objects.create(
            username="30111222", dni="30111222", rol=Usuario.Rol.DOCENTE
        )
        self.docente.set_password(CLAVE)
        self.docente.save()

    def test_login_correcto_devuelve_token_y_rol(self):
        r = self.client.post("/api/auth/login/", {"dni": "30111222", "password": CLAVE}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("token", r.json())
        self.assertEqual(r.json()["rol"], Usuario.Rol.DOCENTE)

    def test_login_password_incorrecta(self):
        r = self.client.post("/api/auth/login/", {"dni": "30111222", "password": "clave-equivocada-000"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_dni_inexistente(self):
        r = self.client.post("/api/auth/login/", {"dni": "99999999", "password": CLAVE}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_usuario_inactivo_no_entra(self):
        self.docente.is_active = False
        self.docente.save(update_fields=["is_active"])
        r = self.client.post("/api/auth/login/", {"dni": "30111222", "password": CLAVE}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create(username="30111333", dni="30111333", rol=Usuario.Rol.FAMILIA)
        self.user.set_password(CLAVE)
        self.user.save()

    def test_logout_sin_token_401(self):
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalida_el_token(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, status.HTTP_401_UNAUTHORIZED)


class PerfilTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create(
            username="43000001", dni="43000001", rol=Usuario.Rol.DOCENTE,
            first_name="Ana", last_name="Pérez", email="ana@x.com",
        )
        self.user.set_password(CLAVE)
        self.user.save()
        self.c = _cliente(self.user)

    def test_me_sin_token_401(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_devuelve_perfil_propio(self):
        r = self.c.get("/api/auth/me/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json()["dni"], "43000001")
        self.assertEqual(r.json()["rol"], Usuario.Rol.DOCENTE)

    def test_me_edita_datos_de_contacto(self):
        r = self.c.patch("/api/auth/me/", {"first_name": "Analía", "email": "nuevo@x.com"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Analía")
        self.assertEqual(self.user.email, "nuevo@x.com")

    def test_me_no_cambia_rol_ni_dni(self):
        # rol/dni son read_only: un intento de cambiarlos se ignora.
        self.c.patch("/api/auth/me/", {"rol": Usuario.Rol.ADMINISTRADOR, "dni": "99999999"}, format="json")
        self.user.refresh_from_db()
        self.assertEqual(self.user.rol, Usuario.Rol.DOCENTE)
        self.assertEqual(self.user.dni, "43000001")


class CambioPasswordPropioTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create(username="44000001", dni="44000001", rol=Usuario.Rol.FAMILIA)
        self.user.set_password(CLAVE)
        self.user.save()
        self.c = _cliente(self.user)

    def test_cambio_correcto(self):
        r = self.c.post(
            "/api/auth/cambiar-password/",
            {"password_actual": CLAVE, "password_nueva": "otra-clave-nueva-789"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("otra-clave-nueva-789"))
        self.assertFalse(self.user.check_password(CLAVE))

    def test_password_actual_incorrecta_400(self):
        r = self.c.post(
            "/api/auth/cambiar-password/",
            {"password_actual": "no-es-la-actual", "password_nueva": "otra-clave-nueva-789"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_nueva_debil_400(self):
        r = self.c.post(
            "/api/auth/cambiar-password/",
            {"password_actual": CLAVE, "password_nueva": "123"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
