from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CambioPasswordPropioSerializer,
    DNIAuthTokenSerializer,
    PerfilSerializer,
)


class LoginDNIView(ObtainAuthToken):
    """POST /api/auth/login/ — login por DNI. Endpoint abierto (ObtainAuthToken
    trae permission_classes vacío)."""

    serializer_class = DNIAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "username": user.username,
                "dni": user.dni,
                "rol": user.rol,
            }
        )


class LogoutView(APIView):
    """POST /api/auth/logout/ — invalida el token del usuario autenticado."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/me/ — el usuario ve y edita SU propio perfil (datos de
    contacto). El objeto es siempre request.user, nunca un id de la URL."""

    serializer_class = PerfilSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CambiarPasswordView(APIView):
    """POST /api/auth/cambiar-password/ — cambio de la propia contraseña."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CambioPasswordPropioSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["password_nueva"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Contraseña actualizada."})
