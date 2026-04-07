import io
from pathlib import Path

from api.common.permissions import IsAuthororOrReadOnly
from api.common.views import AddDeleteRelationMixin, ListRetrieveViewSet
from api.recipes.filters import RecipeFilter
from api.recipes.serializers import (ReadRecipeSerializer,
                                     ShortInfoRecipeSerializer, TagSerializer,
                                     WriteRecipeSerializer)
from django.conf import settings
from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Recipe, RecipeIngredient, ShoppingCart,
                            Tag)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class TagtViewSet(ListRetrieveViewSet):
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


class RecipeViewSet(AddDeleteRelationMixin, viewsets.ModelViewSet):
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
    permission_classes = (IsAuthororOrReadOnly,)
    filter_backends = (DjangoFilterBackend,
                       filters.OrderingFilter)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination
    ordering_fields = ('pub_date',)
    ordering = ('-pub_date',)

    def get_queryset(self):
        """Получает QuerySet с привязкой объектов из связных моделей,
        а также вычисляются два дополнительных поля
        is_favorited и  is_in_shopping_cart."""
        favorites = Favorite.objects.filter(recipe=OuterRef('pk'))
        shopping_carts = ShoppingCart.objects.filter(recipe=OuterRef('pk'))
        return Recipe.objects.all().select_related(
            'author'
        ).prefetch_related(
            'ingredients', 'tags'
        ).annotate(
            is_favorited=Exists(favorites),
            is_in_shopping_cart=Exists(shopping_carts)
        )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def create(self, request, *args, **kwargs):
        """Переопределен метод create, чтобы после создания рецепта
        получить поля is_favorited,is_in_shopping_cart и добавить в ответ."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        queryset = self.get_queryset()
        instance = queryset.get(id=instance.id)
        return Response(ReadRecipeSerializer(
            instance, context=self.get_serializer_context()
        ).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Переопределен метод update, чтобы после обновления рецепта
        получить поля is_favorited,is_in_shopping_cart и добавить в ответ."""

        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        queryset = self.get_queryset()
        instance = queryset.get(id=instance.id)
        return Response(ReadRecipeSerializer(
            instance, context=self.get_serializer_context()
        ).data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """Автоматическое проставление автора.
        При создании рецепта в качетсве автора сохраняется
        пользователь, создающий рецепт."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, pk):
        """Метод возвращает короткую ссылку для рецепта."""
        recipe = self.get_object()
        short_link = recipe.create_short_link()
        full_link = f'/s/{short_link}'
        return Response({'short-link': request.build_absolute_uri(full_link)})

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Обрабатывает запрос к эндпоинту recipes/download_shopping_cart.
        Метод получает список покупок аутентиицированного пользователя,
        сделавшего запрос. Ингредиенты в списке отражаются без повторений
        с суммированным количеством. Метод отрисовывает pdf по шаблону
        и возвращает ответ ввиде pdf-файла для скачивания."""
        recipes_queryset = Recipe.objects.filter(
            shopping_carts__user=request.user
        )
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes_queryset
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        # переводим список ингредиентов в список строк
        full_text = [
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) - '
            f'{ingredient["total_amount"]}'
            for ingredient in ingredients
        ]
        # прописываем путь, где лежат шрифты и регистрируем их.
        font_path = (
            Path(settings.BASE_DIR) / 'static' / 'fonts' / 'DejaVuSans.ttf'
        )
        pdfmetrics.registerFont(TTFont('DejaVuSans', str(font_path)))
        # создаем буфер и документ по готовому шаблону
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        # создаем кастомные ститли для заголова и остального текста
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
        # фомируем документа праграфами(текстом) и отступами
        story = []
        story.append(Paragraph('Список покупок', title_style))
        story.append(Spacer(1, 0.5 * inch))
        for ingredient in full_text:
            story.append(Paragraph(ingredient, text_style))
            story.append(Spacer(1, 0.15 * inch))
        doc.build(story)
        buffer.seek(0)

        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_cart.pdf'
        )

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
            'recipe'
        )

    @shopping_cart.mapping.delete
    def delete_recipe_shopping_cart(self, request, pk):
        """"Аутентифицированный пользователь может
        удалить рецепт из корзины."""
        return self.delete_relation(ShoppingCart, 'recipe')

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
        return self.add_relation(Favorite, ShortInfoRecipeSerializer, 'recipe')

    @favorite.mapping.delete
    def delete_arecipe_favorite(self, request, pk):
        """"Аутентифицированный пользователь может
        удалить рецепт из избранного."""
        return self.delete_relation(Favorite, 'recipe')


def redirect_to_recipe_url(request, short_link: str):
    """При получении короткой ссылки рецепта перенаправляет пользователя
    на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect(
        'api:recipes-detail',
        pk=recipe.id
    )
