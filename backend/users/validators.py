import re

from django.core.exceptions import ValidationError


def check_username(value):
    """Валидирует значение поля username модели User

    Проверяет поле username в модели User
    на соответствие допустимым символам
    и исключает значение 'me' как допустимое значение поля username.
    """

    if value == 'me':
        raise ValidationError(
            'Использовать имя me в качестве username запрещено.'
        )

    incorrect_characters = re.sub(r'[\w.@+-]', '', value)
    if incorrect_characters != '':
        raise ValidationError(
            f'Некорректные символы в имени пользователя:'
            f'{str.join(' ', set(incorrect_characters))}.'
        )

    return value
