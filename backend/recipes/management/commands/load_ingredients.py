"""
Менеджмент команд для загрузки тестовых данных из JSON-файлов
в базу данных проекта

Команда предназначена для первичного наполнения базы данных
ингредиентами.

Использование:
    python manage.py load_ingredints

Ожидаемые файлы:
    ingredients.json

Загрузка выполняется через bulk_create(ignore_conflicts=True),
поэтому повторный запуск не создаёт дубликаты.
"""

from recipes.models import Ingredient

from .base_load_command import BaseLoadDataCommand


class Command(BaseLoadDataCommand):
    help = 'Загруска json данных об ингредиентах в базу данных.'
    file_name = 'ingredients'
    model = Ingredient
