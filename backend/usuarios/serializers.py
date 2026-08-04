from django.contrib.auth import authenticate
from rest_framework import serializers


class DNIAuthTokenSerializer(serializers.Serializer):
    """Valida credenciales de login por DNI. Delega en `authenticate()`, que pasa
    por `DNIBackend` (autentica por DNI y chequea `is_active`). No revela si falló
    el DNI o la contraseña: un único mensaje para ambos casos."""

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
