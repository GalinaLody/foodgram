from django.contrib import admin

from .models import Ingredient


@admin.register(Ingredient)
class InredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'is_active')
    list_editable = ('measurement_unit', 'is_active')
    search_fields = ('name',)
    list_filter = ('measurement_unit', 'is_active')
    list_display_links = ('name',)
    ordering = ('name',)


admin.site.empty_value_display = 'Информация не задана'
