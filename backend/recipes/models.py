from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower

from .constants import (
    INGREDIENTS_MEASUREMENT_UNIT_MAX_LENGTH_CHARFIELD,
    INGREDIENTS_NAME_MAX_LENGTH_CHARFIELD,
    RECIPE_INGREDIENT_MIN_AMOUNT,
    RECIPE_MIN_COOKING_TIME,
    RECIPE_NAME_MAX_LENGTH_CHARFIELD,
    SLICE_OUTPUT_STR_METHOD,
    TAG_NAME_MAX_LENGTH_CHARFIELD,
    TAG_SLUG_MAX_LENGTH_SLUGFIELD,
    USER_MAX_LENGTH_CHARFIELD,
    USER_MAX_LENGTH_EMAILFIELD,
)
from .validators import check_username


class User(AbstractUser):
    """Описывает кастомную модель пользователя.

    Расширяет стандартную модель AbstractUser.
    - переопределено поле username, сделано в качестве уникального
    и обязательного;
    - переопределно поле email, сделано в качестве обязательного и уникального;
    - переопределяет поля first_name и last_name, сделано
    в качестве обязательного;
    - добавлено поле is_subscribed;
    - добавлено поле avatar для хранения фото/изображения пользователя;
    - установлена недопустимость повторной регистрации пользователя.
    """

    username = models.CharField(
        max_length=USER_MAX_LENGTH_CHARFIELD,
        blank=False,
        unique=True,
        validators=(check_username,),
        verbose_name='Никнейм'
    )
    first_name = models.CharField(
        max_length=USER_MAX_LENGTH_CHARFIELD,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USER_MAX_LENGTH_CHARFIELD,
        blank=False,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=USER_MAX_LENGTH_EMAILFIELD,
        unique=True,
        blank=False,
        verbose_name='Email'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        default=None,
        verbose_name='Аватар'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:SLICE_OUTPUT_STR_METHOD]


class Subscriptions(models.Model):
    """Модель подписки на пользователя.

    В модели установлены ограничения, по которым пользователь
    не может подпиаться на самого себя, а также не может повторно подписаться
    на другого пользователя.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscriptions'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='На кого подписан',
        related_name='author_subscriptions'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_subscriptions',
                violation_error_message='Вы уже подписаны на пользователя.'
            ),
            models.CheckConstraint(
                condition=~models.Q(user=models.F('following')),
                name='dont_self_follow',
                violation_error_message='Подписка на себя не допустима.'

            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'


class Ingredient(models.Model):
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
        verbose_name='Наименование'
    )
    measurement_unit = models.CharField(
        max_length=INGREDIENTS_MEASUREMENT_UNIT_MAX_LENGTH_CHARFIELD,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                Lower('name'),
                name='%(app_label)s_%(class)s_unique_name',
                violation_error_message='Такой объект уже существует.'
            ),
        )

    def __str__(self):
        return (
            f'{self.name[:SLICE_OUTPUT_STR_METHOD]}: {self.measurement_unit}'
        )


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
        verbose_name='Время (мин.)'
    )
    image = models.ImageField(
        upload_to='recipies/',
        null=True,
        verbose_name='Изображение'
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
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

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
        # дефолтное related_name получается
        # добавлением к имени модели окончания 's'(favorites, shoppingcarts)
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
