from collections import Counter

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.users.serializers import UserSerializer
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredient, Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class WriteRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели связи Рецепт и Ингредиент.

    Используется для сериализатора создания рецептов WriteRecipeSerializer.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточно модели связи Рецепт и Ингредиенты.

    Используется для сериализатора чтения рецептов ReadRecipeSerializer.
    """

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ShortInfoRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов с сокращенным количеством данный."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
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

    tags = TagSerializer(many=True)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    ingredients = ReadRecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )
    is_favorited = serializers.BooleanField(required=False)
    is_in_shopping_cart = serializers.BooleanField(required=False)
    image = Base64ImageField(required=True,)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time',
            'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'text'
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

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags', 'image',
            'name', 'text',
            'cooking_time'
        )

    def validate_ingredients(self, value):
        """Проверяет, чтобы поле ингредиенты не было пустым,
        все ингредиенты были is_active, не было повторяющихся ингредиентов."""
        ids = [ingredient['ingredient'].id for ingredient in value]
        if not ids:
            raise serializers.ValidationError(
                'Поле с ингредиентами не может быть пустым.'
            )

        count_ingredients = Ingredient.objects.filter(
            id__in=ids, is_active=True
        ).count()
        if len(set(ids)) != count_ingredients:
            raise serializers.ValidationError(
                'Нельзя использовать не активные ингредиенты.'
            )

        counter = Counter(ids)
        doubl_ingredients = []
        for ingredient_id, count in counter.items():
            if count >= 2:
                doubl_ingredients.append(ingredient_id)
        if doubl_ingredients:
            name_ingredients = [
                ingredient.name
                for ingredient in Ingredient.objects.filter(
                    id__in=doubl_ingredients
                )
            ]
            raise serializers.ValidationError(
                f'Ингредиент(ы) {", ".join(name_ingredients)} повторяется.'
            )
        return value

    def validate_tags(self, value):
        """Проверяет, чтобы поле с тегами не было пустым
        и не было повторяющихся тегов."""
        if not value:
            raise serializers.ValidationError(
                'Поле с тегами не может быть пустым.'
            )
        else:
            counter = Counter(value)
            double_tegs = []
            for tag, count in counter.items():
                if count >= 2:
                    double_tegs.append(tag)
            if double_tegs:
                print(double_tegs)
                name_tag = [
                    tag.name for tag in double_tegs
                ]
                raise serializers.ValidationError(
                    f'Тег(и) {", ".join(name_tag)} повторяется.'
                )
        return value

    def validate_image(self, value):
        """Проверяет, чтобы поле image не было пустым."""
        if not value:
            raise serializers.ValidationError('Поле не может быть пустым.')
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        print(validated_data)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)

        if 'ingredients' in validated_data:
            instance.recipe_ingredients.all().delete()
            new_ingredients = validated_data.pop('ingredients')
            for ingredient in new_ingredients:
                RecipeIngredient.objects.create(recipe=instance, **ingredient)

        instance.save()
        return instance

    def to_representation(self, instance):
        """Возвращает данные в формате read-сериализатора рецептов."""
        return ReadRecipeSerializer(instance, context=self.context).data
