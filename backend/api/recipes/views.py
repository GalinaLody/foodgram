from pathlib import Path

from django.db import IntegrityError
from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from rest_framework import exceptions, filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.common.permissions import IsAuthorOrReadOnly
from api.recipes.filters import RecipeFilter
from api.recipes.serializers import (
    ReadRecipeSerializer,
    ShortInfoRecipeSerializer,
    TagSerializer,
    WriteRecipeSerializer,
)
from api.recipes.utils import create_shopping_cart_text
from common.filters import NameSearchFilterBackend
from recipes.models import (
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление API для управления тегами.

    Просмотр(чтение) списка тегов.
    Просмотр(чтение) отдельного тега по id.
    Доступно для всех пользователей.
    Реализован поиск по частичному вхождению
    в начале названия тега(1) и по вхождению в произвольном месте(2).
    В данном случае сортировка ответа от 1 ко 2.
    Реализована сортировка по названию тега.
    """

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.AllowAny,)
    filter_backends = (
        NameSearchFilterBackend,
        filters.OrderingFilter,
    )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Представляет API для управления рецептами.

    Метод PUT не поддерживается.
    Получение списка рецептов, получение конретного рецепта,
    получение короткой ссылки доступны всем пользователям.
    Создание рецепта доступно только аутентифицированному пользователю.
    Редактирование, удаление рецепта доступно только автору рецепта.
    Реализованы методы добавление/удаление рецепта
    в корзину покупок пользователя, а также скачивание пользователем
    списка ингредиентов для покупки.
    Реализованы методы добавление/удаление рецепта
    в Избранное пользователя.
    """

    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering_fields = ('pub_date',)
    ordering = ('-pub_date',)

    def get_queryset(self):
        """Получает QuerySet с привязкой объектов из связных моделей,
        а также вычисляются два дополнительных поля
        is_favorited и  is_in_shopping_cart."""
        recipe_queryset = Recipe.objects.all().select_related(
            'author'
        ).prefetch_related(
            'ingredients', 'tags'
        )
        if self.request.user.is_authenticated:
            favorites = Favorite.objects.filter(
                recipe=OuterRef('pk'), user=self.request.user
            )
            shopping_carts = ShoppingCart.objects.filter(
                recipe=OuterRef('pk'), user=self.request.user
            )
            return recipe_queryset.annotate(
                is_favorited=Exists(favorites),
                is_in_shopping_cart=Exists(shopping_carts)
            )
        return recipe_queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def perform_create(self, serializer):
        """Автоматическое проставление автора.
        При создании рецепта в качетсве автора сохраняется
        пользователь, создающий рецепт."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, pk):
        """Метод возвращает короткую ссылку для рецепта
        на основании id-ключа рецепта."""
        if not Recipe.objects.filter(id=pk).exists():
            raise exceptions.NotFound(f'Рецепт с id={pk} не найден')
        return Response({
            'short-link': request.build_absolute_uri(
                reverse('recipes:redirect', args=[pk])
            )
            })

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Обрабатывает запрос к эндпоинту recipes/download_shopping_cart.
        Метод получает список покупок аутентифицированного пользователя,
        сделавшего запрос. Ингредиенты в списке отражаются без повторений
        с суммированным количеством. Метод отрисовывает pdf по шаблону
        и возвращает ответ ввиде pdf-файла для скачивания."""
        recipes = Recipe.objects.filter(
            shoppingcarts__user=request.user
        ).prefetch_related('tags')

        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')
        shopping_cart_text = create_shopping_cart_text(ingredients, recipes)
        return FileResponse(
            shopping_cart_text,
            as_attachment=True,
            filename='shopping_cart.txt'
        )

    def add_relation(self, model, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError(f'Такой объект модели {model} уже существует.')
        model.objects.create(user=user, recipe=recipe)
        return Response(
            ShortInfoRecipeSerializer(
                recipe, context={'request': self.request}
            ).data,
            status=201
        )

    def delete_relation(self, model, pk):
        get_object_or_404(model, user=self.request.user, recipe_id=pk)
        return Response(status=204)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        """Обрабатывает запрос к эндпоинту recipes/id/shoping_cart.
        Аутентифицированный пользователь может добавить рецепт себе в корзину.
        """
        return self.add_relation(ShoppingCart, pk)

    @shopping_cart.mapping.delete
    def delete_recipe_shopping_cart(self, request, pk):
        """"Аутентифицированный пользователь может
        удалить рецепт из корзины."""
        return self.delete_relation(ShoppingCart, pk)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk):
        """Обрабатывает запрос к эндпоинту recipes/id/favorite.
        Аутентифицированный пользователь может добавить рецепт
        себе в избранное."""
        return self.add_relation(Favorite, pk)

    @favorite.mapping.delete
    def delete_recipe_favorite(self, request, pk):
        """"Аутентифицированный пользователь может
        удалить рецепт из избранного."""
        return self.delete_relation(Favorite, pk)
