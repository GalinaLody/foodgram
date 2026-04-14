from api.common.views import ListRetrieveViewSet
from api.ingredients.serializers import IngredientSerializer
from recipes.models import Ingredient


class IngredientViewSet(ListRetrieveViewSet):
    """Представление API для управления ингредиентами.

    Чтение списка ингредиентов.
    Чтение отдельного ингредиента по id.
    Доступно для всех пользователей.
    Реализован поиск по частичному вхождению
    в начале названия ингредиента(1) и по вхождению в произвольном месте(2).
    В данном случае сортировка ответа от 1 ко 2.
    Реализована сортировка по названию ингредиента.
    Queryset ограничен только активными ингредиентами.
    """

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
