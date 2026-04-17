import re

from django.conf import settings
from django.core.exceptions import ValidationError


def check_username(username):
    """Валидирует значение поля username модели User

    Проверяет поле username в модели User
    на соответствие допустимым символам
    и исключает значение 'me' как допустимое значение поля username.
    """

    if incorrect_characters := re.sub(
        settings.USERNAME_ALLOWED_SIGNS_PATTERN, '', username
    ):
        raise ValidationError(
            'Некорректные символы в '
            'имени пользователя:{}'.format("".join(set(incorrect_characters)))
        )

    return username
