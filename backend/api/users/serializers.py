from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    """Кастомный сериализатор пользователя.

    Используется для переопределения стандартных
    сериализаторов Djoser user и current_user.
    Наследует от BaseUserSerializer,
    добавляя поле 'avatar', 'is_subscribed'.
    """

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = [*DjoserUserSerializer.Meta.fields, 'avatar', 'is_subscribed']
        read_only_fields = fields

    def get_is_subscribed(self, obj_user):
        """Получает значение поля is_subscribed, которого нет в модели."""
        request = self.context['request']
        return (
            not request.user.is_anonymous
            and request.user.subscriptions.filter(following=obj_user).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериалайзер для поля avatar модели User.

    Используется для добавления и удаления аватара.
    """

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для работы с подписками пользователя.

    Наследует от сериализатора UserSerializer.
    Дополнительное поле recipes использует вложенный сериализатор
    ShortInfoRecipeSerializer для вывода сокращенной информаии о рецептах.
    Дополнительтное поле recipes_count вычисляется во вьюсете, если требуется
    получить информацию в отношении большого количества пользователей, и
    вычисляется в сериализаторе, если во вьюсете нет этих данных
    (используется для получения иформации для одного пользователя).
    """

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = [*UserSerializer.Meta.fields, 'recipes', 'recipes_count']
        read_only_fields = fields

    def get_recipes(self, user):
        """Получает поле recipes в формате ShortInfoRecipeSerializer.
        Если в запросе установлен лимит рецептов(параметр recipes_limit),
        возвращает ответ с указанным количестовм рецептов."""
        from api.recipes.serializers import ShortInfoRecipeSerializer
        request = self.context['request']
        recipes = user.recipes.all()
        if request.query_params.get('recipes_limit'):
            recipes_limit = int(request.query_params.get('recipes_limit'))
            recipes = recipes[:recipes_limit]
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
