from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class DNIBackend(ModelBackend):
    """Autentica por DNI. Hereda de ModelBackend user_can_authenticate
    (chequea is_active) y la maquinaria de permisos."""

    def authenticate(self, request, dni=None, password=None, **kwargs):
        if dni is None or password is None:
            return None
        try:
            user = UserModel._default_manager.get(dni=dni)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)  # corre el hasher igual: evita timing attack
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None