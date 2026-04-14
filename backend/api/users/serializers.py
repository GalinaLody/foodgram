from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer,
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Subscriptions

User = get_user_model()


class BaseUserSerializer(DjoserUserSerializer):
    """Базовый сериалайзер модели пользователя.

    Наследует от сериализатора djoser и включает поля
    id, email, username и поля модели User, указанные в
    REQUIRED_FIELDS() модели кастомной модели User
    """


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Кастомный сериализатор для создания пользователя.

    Наследует от сериализатора djoser.
    """


class UserSerializer(BaseUserSerializer):
    """Кастомный сериализатор пользователя.

    Используется для переопределения стандартных
    сериализаторов Djoser user и current_user.
    Наследует от BaseUserSerializer,
    добавляя поле 'avatar', 'is_subscribed'.
    """

    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + (
            'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, obj_user):
        """Получает значение поля is_subscribed, которого нет в модели."""
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return request.user.subscriptions.filter(following=obj_user).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериалайзер для поля avatar модели User.

    Используется для добавления и удаления аватара.
    """

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class SubscribeSerializer(UserSerializer):
    """Сериализатор для создания подписки.

    Наследует от сериализатора UserSerializer.
    Дополнительное поле recipes использует вложенный сериализатор
    ShortInfoRecipeSerializer для вывода сокращенной информаии о рецептах.
    Дополнительтное поле recipes_count вычисляется во вьюсете, если требуется
    получить информацию в отношении большого количества пользователей, и
    вычисляется в сериализаторе, если во вьюсете нет этих данных
    (используется для получения иформации для одного пользователя).
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, user):
        """Получает поле recipes в формате ShortInfoRecipeSerializer.
        Если в запросе установлен лимит рецептов(параметр recipes_limit),
        возвращает ответ с указанным количестовм рецептов."""
        from api.recipes.serializers import ShortInfoRecipeSerializer
        request = self.context['request']
        if request.query_params.get('recipes_limit'):
            recipes_limit = int(request.query_params.get('recipes_limit'))
            recipes = user.recipes.all()[:recipes_limit]
        else:
            recipes = user.recipes.all()
        return ShortInfoRecipeSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, user):
        """Если объект содержит поле recipes_count значение берется
        из объекта, если нет - вычисляется."""
        if hasattr(user, 'recipes_count'):
            return user.recipes_count
        else:
            return user.recipes.count()

    def validate_following(self, new_following):
        """Проверка подписки на самого себя
        и проверка повторной подписки на пользователя.
        Проверяет, чтобы поле запроса following не совпадало с
        с пользователем, отправившим запрос.
        А также проверяет, чтобы пара user-following была уникальной
        в модели Subscriptions."""
        request = self.context['request']
        if new_following == request.user:
            raise serializers.ValidationError(
                'Подписка на самого себя невозможна.'
            )
        if Subscriptions.objects.filter(
            user=request.user, following=new_following
        ).exists():
            raise serializers.ValidationError(
                'Повторная подписка на пользователя невозможна.'
            )
        return new_following
