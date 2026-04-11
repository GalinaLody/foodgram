from core.constants import SLICE_OUTPUT_STR_METHOD
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower
from ingredients.models import Ingredient

from .constants import (RECIPE_INGREDIENT_MIN_AMOUNT, RECIPE_MIN_COOKING_TIME,
                        RECIPE_NAME_MAX_LENGTH_CHARFIELD,
                        TAG_NAME_MAX_LENGTH_CHARFIELD,
                        TAG_SLUG_MAX_LENGTH_SLUGFIELD)


class Tag(models.Model):
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
        verbose_name='Метка',
        unique=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                Lower('name'),
                name='%(app_label)s_%(class)s_unique_name',
                violation_error_message='Такой объект уже существует.'
            ),
        )

    def __str__(self):
        return self.name[:SLICE_OUTPUT_STR_METHOD]


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
        ),
        verbose_name='Время приготовления (мин.)'
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

    @property
    def cooking_time_display(self):
        """Отображение время приготовления с минутами."""
        return f'{self.cooking_time} мин'

    cooking_time_display.fget.short_description = 'Время приготовления'

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
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                RECIPE_INGREDIENT_MIN_AMOUNT,
                message=(
                    f'Количество не может быть меньше '
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
        return f'{self.recipe} {self.ingredient}'


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
        default_related_name = '%(class)ss'
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
