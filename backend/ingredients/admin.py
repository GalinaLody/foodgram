from django.contrib import admin
from django.db.models import Count

from .models import Ingredient


@admin.register(Ingredient)
class InredientAdmin(admin.ModelAdmin):
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


admin.site.empty_value_display = 'Информация не задана'
