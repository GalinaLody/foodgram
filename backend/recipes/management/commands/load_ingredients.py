from recipes.models import Ingredient

from .base_load_command import BaseLoadDataCommand


class Command(BaseLoadDataCommand):
    help = 'Загрузка данных об ингредиентах из json-файла в базу данных.'
    file_name = 'ingredients'
    model = Ingredient
