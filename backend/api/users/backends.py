from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailAuthenticationBackend(ModelBackend):
    """Пользовательская авторизация по email.

    Переопределяет метод авторизации заменяя поле username
    на поле email при осущестлении пользователем входа.
    """

    def authenticate(self, request, **kwargs):
        email = kwargs.get('email') or kwargs.get('username')
        password = kwargs.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
