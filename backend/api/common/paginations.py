from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Кастомный пагинатор.

    Устанавливает размер страницы по умолчанию - 6 объектов.
    Поддерживает параметр limit для изменения размера страницы.
    """

    page_size = 6
    page_size_query_param = 'limit'
