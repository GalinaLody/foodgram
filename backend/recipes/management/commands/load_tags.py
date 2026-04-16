from recipes.models import Tag

from .base_load_command import BaseLoadDataCommand


class Command(BaseLoadDataCommand):
    help = 'Загрузка данных о тегах из json-файла в базу данных.'
    file_name = 'tags'
    model = Tag
