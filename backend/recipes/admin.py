import numpy as np
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.utils.safestring import mark_safe

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


class IsRelationFilter(admin.SimpleListFilter):
    """Базовый фильтр о наличии/отсутствии у пользователя связей."""

    related_name: str
    LOOKUP_CHOICES = (
        ('y', 'есть'),
        ('n', 'нет')
    )

    def lookups(self, request, model_admin):
        return self.LOOKUP_CHOICES

    def queryset(self, request, queryset):
        condition = {f'{self.related_name}__isnull': False}
        if self.value() == 'y':
            return queryset.filter(**condition)
        if self.value() == 'n':
            return queryset.exclude(**condition)


class IsResipeListFilter(IsRelationFilter):
    """Кастомный фильтр о наличии/отсутствию рецептов у пользователя."""
    title = 'Наличие рецептов'
    parameter_name = 'is_recipes'
    related_name = 'recipes'


class IsFollowingListFilter(IsRelationFilter):
    """Кастомный фильтр о наличии/отсутствию подписок у пользователя."""
    title = 'Наличие подписок'
    parameter_name = 'is_following'
    related_name = 'subscriptions'


class IsFollowersListFilter(IsRelationFilter):
    """Кастомный фильтр о наличии/отсутствию подписавшихся на пользователя."""
    title = 'Наличие подписчиков'
    parameter_name = 'is_followers'
    related_name = 'author_subscriptions'


class IsInRecipeListFilter(IsRelationFilter):
    """Кастомный фильтр об использовании/неиспользовании
    ингредиента в рецептах."""
    title = 'Используется в рецепте'
    parameter_name = 'is_in_recipe'
    related_name = 'recipe_ingredients'


class CookingTimeListFilter(admin.SimpleListFilter):
    """Кастомный фильтр для отображения рецептов.

    Фильтр ранжируется по времени приготовления.
    Отражается количество рецептов в каждой группе фильтра.
    Cами пороговые значения времени приготовления рассчитываются по текущему
    набору рецептов.
    """

    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        if recipes.values_list('cooking_time').distinct().count() <= 3:
            return ()
        cooking_time_edges = np.histogram_bin_edges(
            recipes.values_list('cooking_time', flat=True),
            bins=3
        )
        self.time_ranges = {
            'faster': [
                round(cooking_time_edges[0]), round(cooking_time_edges[1])
            ],
            'average': [
                round(cooking_time_edges[1]), round(cooking_time_edges[2])
            ],
            'long': [
                round(cooking_time_edges[2]), round(cooking_time_edges[3])
            ]
        }
        faster_recipe_count = recipes.filter(
            cooking_time__range=self.time_ranges['faster']
        ).count()
        average_recipe_count = recipes.filter(
            cooking_time__range=self.time_ranges['average']
        ).count()
        long_recipe_cont = recipes.filter(
            cooking_time__range=self.time_ranges['long']
        ).count()
        return (
            (
                'faster',
                f'Быстро(до {round(cooking_time_edges[1]) - 1} минут) '
                f'({faster_recipe_count})'
            ),
            (
                'average',
                f'Средне (от {round(cooking_time_edges[1])} до '
                f'{round(cooking_time_edges[2]) - 1} минут) '
                f'({average_recipe_count})'
            ),
            (
                'long',
                f'Долго(больше {round(cooking_time_edges[2])} минут) '
                f'({long_recipe_cont})'
            )
        )

    def queryset(self, request, recipes):
        if self.value() in self.time_ranges:
            return recipes.filter(
                cooking_time__range=self.time_ranges[self.value()]
            )
        return recipes


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
        return recipe.text[:50]

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


class BaseCountRecipesAdminMixin:
    """Общий миксин.

    Аннотирует queryset количеством рецептов.
    Отражает количество рецептов связанных с объектом модели.
    (Количество рецептов с заданным тегом/ингредиентом/userом).
    """

    list_display = ('count_recipes',)
    readonly_fields = ('count_recipes',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            count_recipes=Count('recipes'),
        )

    @admin.display(description='Рецептов')
    def count_recipes(self, obj):
        """Отображает количество рецептов."""
        return obj.count_recipes


@admin.register(User)
class UserAdmin(BaseCountRecipesAdminMixin, BaseUserAdmin):
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
        *BaseCountRecipesAdminMixin.list_display,
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
        *BaseCountRecipesAdminMixin.readonly_fields,
        'following_count',
        'followers_count',
        'post_avatar'
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            count_following=Count('subscriptions', distinct=True),
            count_followers=Count('author_subscriptions', distinct=True)
        )

    @admin.display(description='Подписчиков')
    def following_count(self, user):
        return user.count_following

    @admin.display(description='Подписавшихся')
    def followers_count(self, user):
        return user.count_followers

    @admin.display(description="Полное имя")
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Аватар')
    @mark_safe
    def post_avatar(self, user):
        if user.avatar:
            style = 'object-fit: cover; border-radius: 50%;'  # noqa: E702
            return (
                f'<img src="{user.avatar.url}" height="50" width="50" '
                f'style="{style}" />'
            )
        return ''


@admin.register(Ingredient)
class IngredientAdmin(BaseCountRecipesAdminMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
        *BaseCountRecipesAdminMixin.list_display
    )
    list_editable = ('measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit', IsInRecipeListFilter)
    list_display_links = ('name',)
    ordering = ('name',)
    readonly_fields = (*BaseCountRecipesAdminMixin.readonly_fields,)


@admin.register(Tag)
class TagAdmin(BaseCountRecipesAdminMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        *BaseCountRecipesAdminMixin.list_display
    )
    list_editable = ('slug',)
    search_fields = ('name', 'slug')
    ordering = ('name',)
    readonly_fields = (*BaseCountRecipesAdminMixin.readonly_fields,)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'post_image', 'id', 'name', 'author',
        'get_ingredients', 'get_tags',
        'cooking_time',
        'recipes_count_in_favorites', 'pub_date'
    )
    search_fields = (
        'author__username', 'author__email'
        'name', 'ingredients__name', 'tags__name'
    )
    list_filter = ('author', 'tags', CookingTimeListFilter)
    list_display_links = ('author', 'name')
    filter_horizontal = ('tags',)
    ordering = ('name', 'pub_date')
    readonly_fields = ('recipes_count_in_favorites', 'post_image')

    def get_queryset(self, request):
        return super().get_queryset(
            request
        ).prefetch_related(
            'tags', 'recipe_ingredients'
        ).annotate(
            count_favorites=Count('favorites'),
        )

    @admin.display(description='теги')
    @mark_safe
    def get_tags(self, recipe):
        """Отображение тегов в столбик."""
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='ингредиенты')
    @mark_safe
    def get_ingredients(self, recipe):
        """Отображение ингредиентов с количеством и единицей измерения.
        Все ингредиенты отображаются в столбик."""
        return '<br>'.join(
            f'{recipe_ingredient.ingredient.name} '
            f'{recipe_ingredient.amount} '
            f'{recipe_ingredient.ingredient.measurement_unit} '
            for recipe_ingredient in recipe.recipe_ingredients.all()
        )

    @admin.display(description='В избранном')
    def recipes_count_in_favorites(self, recipe):
        """Отображение количества добавлений рецепта в избранное."""
        return recipe.count_favorites

    @admin.display(description='Картинка')
    @mark_safe
    def post_image(self, recipe):
        """Отображает картинку рецепта,
        object-fit: cover - сохраняет пропорции картинки,
        border-radius: 50%; - скругляет углы."""
        if recipe.image:
            return (
                f'<img src="{recipe.image.url}" height="50" width="50" '
                f'style="object-fit: cover; border-radius: 10%;" />'
            )


class ShoppingCartFavoriteAdmin(admin.ModelAdmin):
    """Базовый класс от которого наследуют ShoppingCartAdmin и FavoriteAdmin"""
    list_display = ('id', 'user', 'recipe')
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
