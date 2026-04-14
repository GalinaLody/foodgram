from collections import Counter

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.users.serializers import UserSerializer
from recipes.constants import (
    RECIPE_INGREDIENT_MIN_AMOUNT,
    RECIPE_MIN_COOKING_TIME,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class WriteRecipeIngredientSerializer(serializers.Serializer):
    """Сериализатор промежуточной модели связи Рецепт и Ингредиент.

    Используется для сериализатора создания рецептов WriteRecipeSerializer.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(min_value=RECIPE_INGREDIENT_MIN_AMOUNT)


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточно модели связи Рецепт и Ингредиенты.

    Используется для сериализатора чтения рецептов ReadRecipeSerializer.
    """

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount')


class ShortInfoRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов с сокращенным количеством данный."""

    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time'
        )
        read_only_fields = (
            'id', 'name',
            'image', 'cooking_time'
        )


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения информации о рецепте.

    Использует вложенные сериализаторы для полей:
    tags, author, ingredients.
    Дополнитено вычисляемые поля is_favorited и is_in_shopping_cart
    имеют булевые значения.
    """

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    ingredients = ReadRecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField(
        required=False, read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        required=False,
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time',
            'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'text'
        )
        read_only_fields = ('id', 'name',
            'image', 'cooking_time',
            'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'text')

    def get_user_recipe_relation_status(self, recipe,
                                        name_field, model):
        """Общий метод получения вычисляемых полей
        is_favorited и is_in_shopping_cart."""
        if hasattr(recipe, name_field):
            return getattr(recipe, name_field)
        request = self.context['request']
        user = request.user
        return (
            user.is_authenticated
            and model.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_is_favorited(self, recipe):
        """Если объект содержит поле is_favorited значение берется
        из объекта, если нет - вычисляется."""
        return self.get_user_recipe_relation_status(
            recipe, 'is_favorited', Favorite
        )

    def get_is_in_shopping_cart(self, recipe):
        """Если объект содержит поле is_in_shopping_cart значение берется
        из объекта, если нет - вычисляется."""
        return self.get_user_recipe_relation_status(
            recipe, 'is_in_shopping_cart', ShoppingCart
        )


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления рецепта.

    Принимает: список id-тегов, список id-ингредиентов и количества,
    картинку, наименование, рецепта, текс, время приготовления.
    Проверяет на наличие повторяющихся ингредиентов.
    Проверяет, чтобы все ингредиенты рецепта были is_active.
    Возвращает данные в формате ReadRecipeSerializer.
    """

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = WriteRecipeIngredientSerializer(many=True, required=True)
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(min_value=RECIPE_MIN_COOKING_TIME)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags', 'image',
            'name', 'text',
            'cooking_time'
        )

    def validate_field(self, ids, model):
        """Общий метод валидации поля (для поля ингредиентов и тегов).
        Проверяет, чтобы поле не было пустым
        и не было повторяющихся элементов."""
        if not ids:
            raise serializers.ValidationError(
                'Поле не может быть пустым.'
            )

        counter = Counter(ids)
        doubl_ids = [
            value_id
            for value_id, count in counter.items()
            if count >= 2
        ]
        if doubl_ids:
            name_object = [
                object.name
                for object in model.objects.filter(
                    id__in=doubl_ids
                )
            ]
            raise serializers.ValidationError(
                f'{name_object} повторяется.'
            )

    def validate_ingredients(self, ingredients):
        """Проверяет, чтобы поле ингредиенты не было пустым,
        не было повторяющихся ингредиентов."""
        ids = [ingredient['ingredient'].id for ingredient in ingredients]
        self.validate_field(ids, Ingredient)
        return ingredients

    def validate_tags(self, tags):
        """Проверяет, чтобы поле с тегами не было пустым
        и не было повторяющихся тегов."""
        self.validate_field(tags, Tag)
        return tags

    def validate_image(self, value):
        """Проверяет, чтобы поле image не было пустым."""
        if not value:
            raise serializers.ValidationError('Поле не может быть пустым.')
        return value

    def create_relations_recipe_ingredient(self, recipe, ingredients):
        """Метод создает объекты модели RecipeIngredient,
        используется в методах create/udate."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe, **ingredient
            ) for ingredient in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.create_relations_recipe_ingredient(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        recipe.recipe_ingredients.all().delete()
        ingredients = validated_data.pop('ingredients')
        self.create_relations_recipe_ingredient(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        """Возвращает данные в формате read-сериализатора рецептов."""
        return ReadRecipeSerializer(instance, context=self.context).data
