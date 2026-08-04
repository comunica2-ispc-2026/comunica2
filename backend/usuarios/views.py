from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DNIAuthTokenSerializer


class LoginDNIView(ObtainAuthToken):
    """POST /api/auth/login/ — login por DNI.

    Devuelve el token y los datos básicos del usuario, incluido el `rol`, que el
    cliente usa como base de su control de acceso. Endpoint abierto: `ObtainAuthToken`
    trae `permission_classes` vacío, así que no lo alcanza el `IsAuthenticated` global.
    """

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
    """POST /api/auth/logout/ — invalida el token del usuario autenticado.

    Requiere token: es el endpoint que ejerce la "API cerrada por defecto"
    (`IsAuthenticated`). Borrar el token corta las credenciales del lado servidor.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
