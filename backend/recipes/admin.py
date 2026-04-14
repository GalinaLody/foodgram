from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscriptions,
    Tag,
    User,
)
from .utils import Percentile


class IsRelationFilter(admin.SimpleListFilter):
    """Базовый фильтр о наличии/отсутствии у пользователя связей."""

    def lookups(self, request, model_admin):
        return (
            ('y', _('есть')),
            ('n', _('нет'))
        )

    def queryset(self, request, queryset):
        condition = {f'{self.related_name}__isnull': False}
        if self.value() == 'y':
            return queryset.filter(**condition)
        if self.value() == 'n':
            return queryset.exclude(**condition)


class IsResipeListFilter(IsRelationFilter):
    """Кастомный фильтр по наличию/отсутствию рецептов у пользователя."""
    title = _('Наличие рецептов')
    parameter_name = 'is_recipes'
    related_name = 'recipes'


class IsFollowingListFilter(IsRelationFilter):
    """Кастомный фильтр по наличию/отсутствию подписок у пользователя."""
    title = _('Наличие подписок')
    parameter_name = 'is_following'
    related_name = 'subscriptions'


class IsFollowersListFilter(IsRelationFilter):
    """Кастомный фильтр по наличию/отсутствию подписавшихся на пользователя."""
    title = _('Наличие подписчиков')
    parameter_name = 'is_followers'
    related_name = 'follower_subscriptions'


class CookingTimeListFilter(admin.SimpleListFilter):
    """Кастомный фильтр для отображения рецептов.

    Фильтр ранжируется по времени приготовления.
    Отражается количество рецептов в каждой группе фильтра.
    Cами пороговые значения времени приготовления рассчитываются по текущему
    набору рецептов.
    """

    title = _('Время приготовления')
    parameter_name = 'cooking_time'

    def __init__(self, request, params, model, model_admin):
        """Через кастомный percentile высчитывает 2 временных порога
        и записывает доп.информацией в __init__, чтобы применять
        в других методах через self."""

        qs = model_admin.get_queryset(request)
        times = qs.aggregate(
            faster_time=Percentile('cooking_time', percentile=0.33),
            average_time=Percentile('cooking_time', percentile=0.66)
        )
        self.faster_time = int(times['faster_time'] or 0)
        self.average_time = int(times['average_time'] or 0)
        super().__init__(request, params, model, model_admin)

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        faster_recipe_count = qs.filter(
            cooking_time__lte=self.faster_time
        ).count()
        average_recipe_count = qs.filter(
            cooking_time__range=[self.faster_time, self.average_time]
        ).count()
        long_recipe_cont = qs.filter(
            cooking_time__gt=self.average_time
        ).count()
        return (
            ('faster', _(
                f'Быстро(до {self.faster_time} минут) ({faster_recipe_count})'
            )),
            ('average', _(
                f'Средне (от {self.faster_time} до {self.average_time} минут) '
                f'({average_recipe_count})'
            )),
            ('long', _(
                f'Долго(больше {self.average_time} минут) ({long_recipe_cont})'
            ))
        )

    def queryset(self, request, queryset):
        if self.value() == 'faster':
            return queryset.filter(cooking_time__lte=self.faster_time)
        if self.value() == 'average':
            return queryset.filter(
                cooking_time__range=[self.faster_time, self.average_time]
            )
        if self.value() == 'long':
            return queryset.filter(cooking_time__gt=self.average_time)


class SubscriptionsInline(admin.StackedInline):
    model = Subscriptions
    extra = 0
    fk_name = 'user'


class RecipeInline(admin.TabularInline):
    model = Recipe
    extra = 0
    fields = ('name', 'get_ingredients', 'short_text', 'tags', 'cooking_time')
    readonly_fields = ('short_text', 'get_ingredients')
    autocomplete_fields = ('tags',)
    can_delete = True

    @admin.display(description='текст')
    def short_text(self, recipe):
        """Отображение текста рецепта в списке сокращенно."""
        return recipe.text[:50] + '...'

    @admin.display(description='ингредиенты')
    def get_ingredients(self, recipe):
        """Отображение ингредиентов в списке."""
        return ', '.join(
            recipe_ingredient.ingredient.name
            for recipe_ingredient in recipe.recipe_ingredients.all()
        )


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    fields = ('ingredient', 'amount', 'measurement_unit')
    readonly_fields = ('measurement_unit',)
    autocomplete_fields = ('ingredient',)
    can_delete = True

    @admin.display(description='единица измерения')
    def measurement_unit(self, recipe_ingredient):
        """Отображение единицы измерения ингредиента в рецепте."""
        return recipe_ingredient.ingredient.measurement_unit


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': (
            'first_name', 'last_name',
            'email', 'avatar', 'post_avatar'
        )}),
        ('Статус пользователя', {'fields': (
            'is_superuser', 'is_staff', 'is_active'
        )}),
        ('Даты регистрации и входа', {'fields': (
            'last_login', 'date_joined'
        )}),
    )
    list_display = (
        'id',
        'post_avatar',
        'username',
        'full_name',
        'email',
        'recipes_count',
        'following_count',
        'followers_count'
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_display_links = (
        'username',
        'email'
    )
    list_filter = (
        IsResipeListFilter,
        IsFollowingListFilter,
        IsFollowersListFilter
    )
    ordering = ('username',)
    inlines = (SubscriptionsInline, RecipeInline)
    readonly_fields = (
        'recipes_count', 'following_count',
        'followers_count', 'post_avatar'
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            count_recipes=Count('recipes', distinct=True),
            count_following=Count('subscriptions', distinct=True),
            count_followers=Count('follower_subscriptions', distinct=True)
        )

    @admin.display(description='Количество рецептов')
    def recipes_count(self, user):
        """Отображение количество рецептов пользователя."""
        return user.count_recipes

    @admin.display(description='Количество подписчиков(following)')
    def following_count(self, user):
        """Отображение количества подписчиков пользователя."""
        return user.count_following

    @admin.display(description='Количество подписавшихся(followers)')
    def followers_count(self, user):
        """Отображение количества подписок на пользователя."""
        return user.count_followers

    @admin.display(description="Полное имя")
    def full_name(self, user):
        """Отображает ФИО: irst_name+last_name."""
        return f'{user.first_name} {user.last_name}'.upper()

    @mark_safe
    def post_avatar(self, user):
        """Отображает аватар как картинку,
        object-fit: cover - сохраняет пропорции картинки,
        border-radius: 50%; - аватар в форме овала."""
        if user.avatar:
            style = 'object-fit: cover; border-radius: 50%;'  # noqa: E702
            return (
                f'<img src="{user.avatar.url}" height="50" width="50" '
                f'style="{style}" />'
            )
        return 'Аватар не загружен'

    post_avatar.short_description = 'Аватар'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'count_recipes')
    list_editable = ('measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_display_links = ('name',)
    ordering = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            count_ingredients=Count('recipes')
        )

    @admin.display(description='Рецептов с ингредиентом')
    def count_recipes(self, ingredient):
        """Отображение количества рецептов с заданным ингредиентом."""
        return ingredient.count_ingredients


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'count_recipes')
    list_editable = ('slug',)
    search_fields = ('name', 'slug')
    ordering = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            count_recipes=Count('recipes'),
        )

    @admin.display(description='Количество рецептов с тегом')
    def count_recipes(self, tag):
        """Отображение количество рецептов с тегом."""
        return tag.count_recipes


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'post_image', 'id', 'name', 'author',
        'get_ingredients', 'get_tags',
        'cooking_time_display',
        'recipes_count_in_favorites'
    )
    search_fields = (
        'author__username', 'name',
        'ingredients__name', 'tags__name'
    )
    list_filter = ('author', CookingTimeListFilter)
    list_display_links = ('author', 'name')
    filter_horizontal = ('tags',)
    ordering = ('name',)
    readonly_fields = ('recipes_count_in_favorites', 'post_image')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related(
            'tags', 'recipe_ingredients'
        ).annotate(
            count_favorites=Count('favorites'),
        )

    @admin.display(description='теги')
    def get_tags(self, recipe):
        """Отображение тегов в столбик."""
        return format_html(',<br>'.join(tag.name for tag in recipe.tags.all()))

    @admin.display(description='ингредиенты')
    def get_ingredients(self, recipe):
        """Отображение ингредиентов с количеством и единицей измерения.
        Все ингредиенты отображаются в столбик."""
        return format_html(
            ',<br>'.join(
                f'{recipe_ingredient.ingredient.name} '
                f'{recipe_ingredient.amount} '
                f'{recipe_ingredient.ingredient.measurement_unit} '
                for recipe_ingredient in recipe.recipe_ingredients.all()
            )
        )

    @admin.display(description='В избранном')
    def recipes_count_in_favorites(self, recipe):
        """Отображение количества добавлений рецепта в избранное."""
        return recipe.count_favorites

    @mark_safe
    def post_image(self, recipe):
        """Отображает картинку рецепта,
        object-fit: cover - сохраняет пропорции картинки,
        border-radius: 50%; - скругляет углы."""
        if recipe.image:
            style = 'object-fit: cover; border-radius: 10%;'  # noqa: E702
            return (
                f'<img src="{recipe.image.url}" height="50" width="50" '
                f'style="{style}" />'
            )

    post_image.short_description = 'Картинка'


class ShoppingCartFavoriteAdmin(admin.ModelAdmin):
    """Базовый класс от которого наследуют ShoppingCartAdmin и FavoriteAdmin"""
    list_display = ('user', 'recipe')
    list_display_links = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    ordering = ('user__username',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(ShoppingCartFavoriteAdmin):
    pass


@admin.register(Favorite)
class FavoriteAdmin(ShoppingCartFavoriteAdmin):
    pass


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    search_fields = ('user__username', 'following__username')
    list_filter = ('user', 'following')
    list_display_links = ('user', 'following')
    autocomplete_fields = ('following',)
    ordering = ('user__username',)


admin.site.empty_value_display = 'Информация не задана'
