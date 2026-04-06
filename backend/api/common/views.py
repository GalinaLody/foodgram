from django.db import IntegrityError
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .filters import NameSearchFilterBackend


class ListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
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


class AddDeleteRelationMixin:
    """Миксин добавляет метод добавления/удаления связи в модель отношений.

    Модели Favorite, Shoppinh_cart, Subschriben содержат связь
    между существующими и валидированными объектами других моделей.
    Метод add_relation добавляет связь в соответсвующую модель.
    Метод delete_relation удаляет уже существующую связь из модели.
    """

    def add_relation(self, model, serializer_class, field_name):
        user = self.request.user
        obj = self.get_object()
        try:
            model.objects.create(user=user, **{field_name: obj})
            return Response(
                serializer_class(obj, context={'request': self.request}).data,
                status=201
            )
        except IntegrityError:
            return Response(status=400)

    def delete_relation(self, model, field_name):
        user = self.request.user
        obj = self.get_object()
        deleted_count, details = model.objects.filter(
            user=user, **{field_name: obj}
        ).delete()
        if deleted_count == 0:
            return Response(status=400)
        return Response(status=204)
