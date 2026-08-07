"""Serializers de `usuarios`.

- `DNIAuthTokenSerializer` (HU-01): login por DNI.
- `PerfilSerializer` (HU-02): el usuario ve/edita SU perfil. rol/dni/cargo/username
  son de solo lectura (los administra el admin, HU-03); el usuario solo cambia sus
  datos de contacto.
- `CambioPasswordPropioSerializer` (HU-02): cambio de la PROPIA contraseña,
  exigiendo la actual. Distinto del reset-password del admin (HU-03), que no la pide.
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Usuario


def _validar_password(password, *, usuario):
    """Corre los AUTH_PASSWORD_VALIDATORS de settings (minimo, comun, numerica,
    similaridad con atributos). Traduce el ValidationError de Django al de DRF
    para que salga 400 y no 500."""
    try:
        validate_password(password, user=usuario)
    except DjangoValidationError as e:
        raise serializers.ValidationError(list(e.messages))


class DNIAuthTokenSerializer(serializers.Serializer):
    dni = serializers.CharField(write_only=True)
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False, write_only=True
    )

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            dni=attrs.get("dni"),
            password=attrs.get("password"),
        )
        if not user:
            raise serializers.ValidationError(
                "No pudimos autenticar con ese DNI y contraseña.", code="authorization"
            )
        attrs["user"] = user
        return attrs


class PerfilSerializer(serializers.ModelSerializer):
    """El perfil propio del usuario logueado. Lo editable son los datos de
    contacto; rol/dni/cargo/username los gobierna la administracion (HU-03)."""

    rol_display = serializers.CharField(source="get_rol_display", read_only=True)
    cargo_display = serializers.CharField(source="get_cargo_display", read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id", "username", "dni",
            "rol", "rol_display", "cargo", "cargo_display",
            "first_name", "last_name", "email",
        ]
        read_only_fields = ["id", "username", "dni", "rol", "cargo"]


class CambioPasswordPropioSerializer(serializers.Serializer):
    """Cambio de la propia contraseña: exige la actual (a diferencia del reset del
    admin). La vista pasa el usuario por contexto."""

    password_actual = serializers.CharField(
        write_only=True, style={"input_type": "password"}, trim_whitespace=False
    )
    password_nueva = serializers.CharField(
        write_only=True, style={"input_type": "password"}, trim_whitespace=False
    )

    def validate_password_actual(self, value):
        if not self.context["user"].check_password(value):
            raise serializers.ValidationError("La contraseña actual no es correcta.")
        return value

    def validate_password_nueva(self, value):
        _validar_password(value, usuario=self.context["user"])
        return value
