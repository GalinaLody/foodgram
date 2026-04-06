from django.db import models

from core.models import NameBaseModel
from .constants import (
    INGREDIENTS_NAME_MAX_LENGTH_CHARFIELD,
    INGREDIENTS_MEASUREMENT_UNIT_MAX_LENGTH_CHARFIELD
)


class Ingredient(NameBaseModel):
    """Описывает модель Ингредиенты.

    Модель наследует от базовой модели NameBaseModel сортировку по name,
    UniqueConstraint по name и метод str.
    Поля name и measurement_unit обязательны.
    Поле name проверяется на уникальность, игнорируя регистры.
    Поле is_active имеет значение по умолчанию True. На базе данного поля
    реализована логика перевода ингредиента в "неактивное" состояние
    при попытке его удаления и наличии его связи с рецептом.
    """

    name = models.CharField(
        max_length=INGREDIENTS_NAME_MAX_LENGTH_CHARFIELD,
        unique=True,
        verbose_name='Наименование'
    )
    measurement_unit = models.CharField(
        max_length=INGREDIENTS_MEASUREMENT_UNIT_MAX_LENGTH_CHARFIELD,
        verbose_name='Единица измерения'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
