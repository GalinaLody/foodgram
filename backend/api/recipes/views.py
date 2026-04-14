import io
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
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.common.permissions import IsAuthorOrReadOnly
from api.common.views import ListRetrieveViewSet
from api.recipes.filters import RecipeFilter
from api.recipes.serializers import (
    ReadRecipeSerializer,
    ShortInfoRecipeSerializer,
    TagSerializer,
    WriteRecipeSerializer,
)
from api.recipes.utils import create_shopping_cart_text
from recipes.models import (
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class TagViewSet(ListRetrieveViewSet):
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
        if Recipe.objects.filter(id=pk).exists():
            return Response({
                'short-link': request.build_absolute_uri(
                    reverse('recipes:redirect', kwargs={'recipe_id': pk})
                )
            })
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

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
        recipes_queryset = Recipe.objects.filter(
            shoppingcarts__user=request.user
        ).prefetch_related('tags')

        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes_queryset
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        recipes = (
            recipes_queryset
            .values('name', 'author__username')
            .prefetch_related('tags')
        )
        # вызываем кастомную фукцию для создания списка в текстовом формате.
        shopping_cart_text = create_shopping_cart_text(ingredients, recipes)
        # прописываем путь, где лежат шрифты и регистрируем их.
        font_path = Path(__file__).parent / 'fonts' / 'DejaVuSans.ttf'
        pdfmetrics.registerFont(TTFont('DejaVuSans', str(font_path)))
        # создаем буфер и документ по готовому шаблону
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        # создаем кастомные стили для заголова и остального текста
        title_style = ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            alignment=1,
            fontName='DejaVuSans',
            fontSize=18,
            spaceAfter=12
        )
        text_style = ParagraphStyle(
            name='CustomText',
            parent=styles['Normal'],
            fontName='DejaVuSans',
            fontSize=12,
            leading=14
        )
        # фомируем документа праграфами и отступами
        doc.build([
            Paragraph('Список покупок', title_style),
            Spacer(1, 0.5 * inch),
            *[
                elem
                for line in shopping_cart_text.splitlines()
                for elem in (
                    Paragraph(line or '&nbsp;', text_style),
                    Spacer(1, 0.15 * inch)
                )
            ]
        ])
        buffer.seek(0)

        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_cart.pdf'
        )

    def add_relation(self, model, serializer_class, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            model.objects.create(user=user, recipe=recipe)
            return Response(
                serializer_class(
                    recipe, context={'request': self.request}
                ).data,
                status=201
            )
        except IntegrityError:
            return Response(status=400)

    def delete_relation(self, model, pk):
        user = self.request.user
        deleted_count, _ = model.objects.filter(
            user=user, recipe_id=pk
        ).delete()
        if deleted_count == 0:
            return Response(status=400)
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
        return self.add_relation(
            ShoppingCart,
            ShortInfoRecipeSerializer,
            pk
        )

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
        return self.add_relation(Favorite, ShortInfoRecipeSerializer, pk)

    @favorite.mapping.delete
    def delete_recipe_favorite(self, request, pk):
        """"Аутентифицированный пользователь может
        удалить рецепт из избранного."""
        return self.delete_relation(Favorite, pk)
