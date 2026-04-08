import re

from django.core.exceptions import ValidationError


def check_tag_slug(value):
    """Валидирует значение поля slug модели Tag

    Проверяет поле slug в модели Tag
    на соответствие допустимым символам.
    """

    incorrect_characters = re.sub(r'^[-a-zA-Z0-9_]+$', '', value)
    if incorrect_characters != '':
        raise ValidationError(
            f'Некорректные символы в slug тега: '
            f'{str.join(" ", set(incorrect_characters))}.'
        )

    return value
