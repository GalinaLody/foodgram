from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.permissions import CurrentUserOrAdmin as DjoserCurrentUserOrAdmin
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.users.serializers import AvatarSerializer, SubscribeSerializer
from recipes.models import Subscriptions

User = get_user_model()


class FoodgramUserViewSet(DjoserUserViewSet):
    """API для работы с пользователем и его подписками.

    Наследует от представления djoser UserViewSet и
    дополняет его методом изменения/удаления аватара пользователя
    по эндпоинту users/me/avatar(доступно только текущему пользователю).
    Список всех пользователей, а также получение конкретного пользователя
    по id доступно всем пользователям(для данных операций переопределены
    права доступа djosera).
    Управляет подписками текущего пользователя: просмотр собственного списка
    подписок,добавление другого пользователя в подписки,
    удаление пользователя из подписок.
    Добавление/удаление пользователей осуществляется с помощью
    методов add_relation и delete_relation кастомного
    миксина AddDeleteRelationMixin.
    """

    pagination_class = LimitOffsetPagination
    queryset = User.objects.all()

    def get_permissions(self):
        """Переопределяет права доступа djoser для GET-запросов
        к /users/ и /users/id/ на 'доступно для всех'
        (было только для авторизованных)."""
        permissions = super().get_permissions()
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return permissions

    @action(
        detail=False,
        methods=('put',),
        url_path='me/avatar',
        permission_classes=(DjoserCurrentUserOrAdmin,)
    )
    def avatar(self, request):
        """Добавляет аватар пользователя."""
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаляет аватар пользователя"""
        user = self.request.user
        if user.avatar:
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Выводит список подписок текущего пользователя
        по эндпоинту /subscriptions."""
        obj = User.objects.filter(follower_subscriptions__user=request.user)
        page = self.paginate_queryset(obj)
        serializer = SubscribeSerializer(
            page, many=True,
            context={'request': self.request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Создает подписку текущего пользоватея на выбранного пользователя
        по эндпоинту /subscribe."""
        user = self.request.user
        user_following = get_object_or_404(User, id=id)
        try:
            Subscriptions.objects.create(user=user, following=user_following)
            return Response(
                SubscribeSerializer(
                    user_following,
                    context={'request': self.request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        """Удаляет подписку текущего пользоватея на другого пользователя
        по эндпоинту /subscribe."""
        user = self.request.user
        deleted_count, __ = Subscriptions.objects.filter(
            user=user, following_id=id
        ).delete()
        if deleted_count == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)
