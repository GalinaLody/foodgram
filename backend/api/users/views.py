from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.permissions import CurrentUserOrAdmin as DjoserCurrentUserOrAdmin
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.common.paginations import PageLimitPagination
from api.users.serializers import AvatarSerializer, SubscriptionsSerializer
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

    pagination_class = PageLimitPagination
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return super().get_permissions()

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
        if not user.avatar:
            raise exceptions.ValidationError(
                f'У пользователя {user.username} нет аватара.'
            )
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
        return self.get_paginated_response(
            SubscriptionsSerializer(
                self.paginate_queryset(
                    User.objects.filter(
                        author_subscriptions__user=request.user
                    )
                ), many=True,
                context={'request': self.request}
            ).data
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Создает подписку текущего пользоватея на выбранного пользователя
        по эндпоинту /subscribe."""
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise exceptions.ValidationError(
                'Подписка на самого себя невозможна.'
            )
        elif Subscriptions.objects.filter(
            user=user, following=author
        ).exists():
            raise exceptions.ValidationError(
                f'Подписка на пользователя{user.username} уже существует.'
            )
        Subscriptions.objects.create(user=user, following=author)
        return Response(
            SubscriptionsSerializer(
                author,
                context={'request': self.request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscriptions(self, request, id):
        """Удаляет подписку текущего пользователя на другого пользователя
        по эндпоинту /subscribe."""
        get_object_or_404(
            Subscriptions, user=self.request.user, following_id=id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
