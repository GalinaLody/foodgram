from api.common.views import AddDeleteRelationMixin
from django.contrib.auth import get_user_model
from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscriptions

from .serializers import AvatarSerializer, SubscribeSerializer

User = get_user_model()


class MyUserViewSet(AddDeleteRelationMixin, UserViewSet):
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
        if self.action == 'list' or self.action == 'retrieve':
            return (AllowAny(),)
        return permissions

    @action(
        detail=False,
        methods=('put',),
        url_path='me/avatar',
        permission_classes=(CurrentUserOrAdmin,)
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
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Выводит список подписок текущего пользователя
        по эндпоинту /subscriptions."""
        current_user = request.user
        obj = User.objects.filter(follower_subscriptions__user=current_user)
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
        return self.add_relation(
            Subscriptions,
            SubscribeSerializer,
            'following'
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        """Удаляет подписку текущего пользоватея на другого пользователя
        по эндпоинту /subscribe."""
        return self.delete_relation(Subscriptions, 'following')
