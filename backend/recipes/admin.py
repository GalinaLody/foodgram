from django.contrib import admin

from .models import Favorite, Recipe, RecipeIngredient, ShoppingCart, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    fields = ('ingredient', 'amount', 'measurement_unit')
    readonly_fields = ('measurement_unit',)
    autocomplete_fields = ('ingredient',)
    can_delete = True

    @admin.display(description='единица измерения')
    def measurement_unit(self, obj):
        """Отображение единицы измерения ингредиента в рецепте."""
        return obj.ingredient.measurement_unit


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_recipe')
    list_editable = ('slug',)
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    ordering = ('name',)

    @admin.display(description='recipies')
    def get_recipe(self, obj):
        return [recipe.name for recipe in obj.recipes.all()]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'author', 'name',
        'get_ingredients', 'short_text',
        'get_tags', 'cooking_time_display_min',
        'short_link', 'recipes_count_in_favorites'
    )
    search_fields = (
        'author__username', 'name', 'ingredients__name',
        'tags__name', 'cooking_time_display_min'
    )
    list_filter = ('author', 'name', 'ingredients', 'tags', 'cooking_time')
    list_display_links = ('author', 'name')
    filter_horizontal = ('tags',)
    ordering = ('name',)
    readonly_fields = ('recipes_count_in_favorites',)

    @admin.display(description='теги')
    def get_tags(self, obj):
        """Отображение тегов в списке."""
        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='ингредиенты')
    def get_ingredients(self, obj):
        """Отображение ингредиентов в списке."""
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    @admin.display(description='текст')
    def short_text(self, obj):
        """Отображение текста рецепта в списке сокращенно."""
        return obj.text[:50] + '...'

    @admin.display(description='время приготовления')
    def cooking_time_display_min(self, obj):
        """Отображение время приготовления в списке с минутами."""
        return f'{obj.cooking_time} мин.'

    @admin.display(description='Количество добавлений в избранное')
    def recipes_count_in_favorites(self, obj):
        """Отображение количества добавлений рецепта в избранное."""
        return obj.favorites.count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    ordering = ('user__username',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    ordering = ('user__username',)


admin.site.empty_value_display = 'Информация не задана'
