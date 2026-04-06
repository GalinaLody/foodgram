from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import Recipe

from .models import Subscriptions, User


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
            'email', 'avatar'
        )}),
        ('Статус пользователя', {'fields': (
            'is_superuser', 'is_staff', 'is_active'
        )}),
        ('Даты регистрации и входа', {'fields': (
            'last_login', 'date_joined'
        )}),
    )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
        'recipes_count'
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
    ordering = ('username',)
    inlines = (SubscriptionsInline, RecipeInline)
    readonly_fields = ('recipes_count',)

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        """Отображение количество рецептов пользователя в списке."""
        return obj.recipes.count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = ('user', 'following')
    list_filter = ('user', 'following')
    list_display_links = ('user', 'following')
    autocomplete_fields = ('following',)
    ordering = ('user__username',)


admin.site.empty_value_display = 'Информация не задана'
