from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from recipes.models import Recipe
from users.models import Subscriptions, User


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
    def short_text(self, obj):
        """Отображение текста рецепта в списке сокращенно."""
        return obj.text[:50] + '...'

    @admin.display(description='ингредиенты')
    def get_ingredients(self, obj):
        """Отображение ингредиентов в списке."""
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': (
            'first_name', 'last_name',
            'email', 'post_avatar'
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
    list_editatable = ('password',)
    list_filter = (
        IsResipeListFilter,
        IsFollowingListFilter,
        IsFollowersListFilter
    )
    ordering = ('username',)
    inlines = (SubscriptionsInline, RecipeInline)
    readonly_fields = ('recipes_count', 'following_count', 'followers_count')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            count_recipes=Count('recipes'),
            count_following=Count('subscriptions'),
            count_followers=Count('follower_subscriptions')
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
        border-radius: 50%; - скругляет углы."""
        if user.avatar:
            style = 'object-fit: cover; border-radius: 50%;'  # noqa: E702
            return (
                f'<img src="{user.avatar.url}" height="50" width="50" '
                f'style="{style}" />'
            )
        return 'Аватар не загружен'

    post_avatar.short_description = 'Аватар'


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    search_fields = ('user', 'following')
    list_filter = ('user', 'following')
    list_display_links = ('user', 'following')
    autocomplete_fields = ('following',)
    ordering = ('user__username',)


admin.site.empty_value_display = 'Информация не задана'
