from rest_framework import filters
from django.db.models import Q, Case, When


class NameSearchFilterBackend(filters.BaseFilterBackend):
    """Кастомный фильтр поиска по полю name.

    Осуществляет поиск по вхождению в начале name и
    поиск по вхождению в произвольном месте поля name.
    Результат сортируется от вхождения в начало до вждения
    в произвольном месте.
    """

    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('name'):
            value = request.query_params['name']
            return queryset.filter(
                Q(name__istartswith=value) | Q(name__icontains=value)
            ).annotate(priority=Case(
                When(name__istartswith=value, then=1),
                When(name__icontains=value, then=2)
            )).order_by('priority', 'name')
        else:
            return queryset
