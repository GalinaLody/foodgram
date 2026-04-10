import re

from django.conf import settings
from django.core.exceptions import ValidationError


def check_username(username):
    """Валидирует значение поля username модели User

    Проверяет поле username в модели User
    на соответствие допустимым символам
    и исключает значение 'me' как допустимое значение поля username.
    """

    incorrect_characters = re.sub(
        settings.USERNAME_ALLOWED_SIGNS, '', username
    )
    if incorrect_characters:
        raise ValidationError(
            f'Некорректные символы в имени пользователя: '
            f'{", ".join(set(incorrect_characters))}.'
        )

    return username
