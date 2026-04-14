from rest_framework import filters
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import NameSearchFilterBackend


class ListRetrieveViewSet(ReadOnlyModelViewSet):
    """Предоставляет базовый viewset для операций с объектом.

    Возвращает список объектов (для обработки GET-запроса).
    Возвращает отдельный объект (для обработки GET-запроса).
    Права доступа для всех.
    Реализован поиск по частичному вхождению
    в начале поля name.
    """

    permission_classes = (AllowAny,)
    filter_backends = (
        NameSearchFilterBackend,
        filters.OrderingFilter,
    )
    pagination_class = None
