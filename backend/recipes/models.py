from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.http import int_to_base36

from core.constants import SLICE_OUTPUT_STR_METHOD
from core.models import NameBaseModel
from ingredients.models import Ingredient

from .constants import (RECIPE_INGREDIENT_MIN_AMOUNT, RECIPE_MAX_COOKING_TIME,
                        RECIPE_MIN_COOKING_TIME,
                        RECIPE_NAME_MAX_LENGTH_CHARFIELD,
                        RECIPE_SHORT_LINK_MAX_LENGTH_CHARFIELD,
                        TAG_NAME_MAX_LENGTH_CHARFIELD,
                        TAG_SLUG_MAX_LENGTH_SLUGFIELD)
from .validators import check_tag_slug


class Tag(NameBaseModel):
    """Описывает модель Тега для рецепта.

    Поля name и slug уникальны и обязательны.
    Модель наследует от базовой модели NameBaseModel сортировку по name,
    UniqueConstraint по name и метод str.
    """

    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH_CHARFIELD,
        unique=True,
        verbose_name='Наименование'
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH_SLUGFIELD,
        verbose_name='Слаг',
        unique=True,
        null=True,
        validators=(check_tag_slug,)
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    """Описывает модель Рецепта.

    - все поля, кроме поля short_link обязательны к заполнению;
    - модель связа с моделями User, Tag, Ingredient;
    - для поля cooking_time установлено минимальное значение
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH_CHARFIELD,
        verbose_name='Название'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        upload_to='recipies/',
        null=True,
        verbose_name='Изображение'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                RECIPE_MIN_COOKING_TIME,
                message=(
                    f'Время приготовления не может быть меньше'
                    f'{RECIPE_MIN_COOKING_TIME} минуты.'
                )
            ),
            MaxValueValidator(
                RECIPE_MAX_COOKING_TIME,
                message=(
                    f'Время приготовления не ожет быть больше'
                    f'{RECIPE_MAX_COOKING_TIME} минут.'
                )
            )
        ),
        verbose_name='Время приготовления (мин.)'
    )
    short_link = models.CharField(
        max_length=RECIPE_SHORT_LINK_MAX_LENGTH_CHARFIELD,
        null=True,
        unique=True,
        verbose_name='Короткая ссылка'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-pub_date',)

    def create_short_link(self):
        """Если короткой сслыки нет, кодирует id объекта в base36
        и записывает в поле short_link, которое используется
        для формирования короткой ссылки.
        Если короткая ссылка уже записана, возвращает ее."""
        if not self.short_link:
            self.short_link = int_to_base36(self.id)
            self.save(update_fields=['short_link'])
        return self.short_link

    def __str__(self):
        return self.name[:SLICE_OUTPUT_STR_METHOD]


class RecipeIngredient(models.Model):
    """Промежуточная модель.

    Необходима для связи ManyToMany между моделями Ingredient и Recipe.
    В поле amount хранится дополнительная информация о количестве ингредиента
    в конкретном рецепте. Данное поле также имеет
    минимальное ограничение единицы измерения.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
       validators=(
            MinValueValidator(
                RECIPE_INGREDIENT_MIN_AMOUNT,
                message=(
                    f'Количество не может быть меньше'
                    f'{RECIPE_INGREDIENT_MIN_AMOUNT} единицы измерения.'
                )
            ),
        ),
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'[:SLICE_OUTPUT_STR_METHOD]


class UserRecipeBaseModel(models.Model):
    """Абстрактный класс для общих полей моделей Shopping_cart и Favorite"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique_name',
                violation_error_message='Такой рецепт уже добавлен.'

            ),
        )

    def __str__(self):
        return f'{self.user} {self.recipe}'[:SLICE_OUTPUT_STR_METHOD]


class ShoppingCart(UserRecipeBaseModel):
    """Модель Список покупок.

    Наследует поля user и recipe у модели UserRecipeBaseModel.
    Описывает список рецептов пользователя отправленных в корзину.
    В модели установлено ограничение на повторное добавление пользователем
    рецепта в корзину.
    """

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_carts'


class Favorite(UserRecipeBaseModel):
    """Модель Избранное.

    Наследует поля user и recipe у модели UserRecipeBaseModel
    Описывает список избранных рецептов пользователя.
    В модели установлено ограничение на повторное добавление пользователем
    рецепта в избранное
    """

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'
