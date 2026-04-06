
import django_filters
from django_filters.widgets import BooleanWidget
from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """Кастомный фильтр для рецептов.

    Фильтрует по полям автор, теги, а также по
    дополнительным полям вне модели is_favorited
    и is_in_shopping_cart.
    """

    tags = django_filters.CharFilter(method='filter_tag_slug')
    is_favorited = django_filters.BooleanFilter(
        widget=BooleanWidget(),
        method='filter_boolean_value'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        widget=BooleanWidget(),
        method='filter_boolean_value'
    )

    class Meta:
        model = Recipe
        fields = (
            'author', 'tags',
            'is_favorited', 'is_in_shopping_cart'
        )

    def filter_boolean_value(self, queryset, name, value):
        field_name_value = {name: value}
        if value is not None:
            return queryset.filter(**field_name_value)
        return queryset

    def filter_tag_slug(self, queryset, name, value):
        if value:
            value = self.request.query_params.getlist('tags')
            return queryset.filter(tags__slug__in=value).distinct()
        return queryset
