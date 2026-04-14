"""
Менеджмент команд для загрузки тестовых данных из JSON-файлов
в базу данных проекта

Команда предназначена для первичного наполнения базы данных
тегами.

Использование:
    python manage.py load_tags

Ожидаемые файлы:
    tags.json

Загрузка выполняется через bulk_create(ignore_conflicts=True),
поэтому повторный запуск не создаёт дубликаты.
"""

from recipes.models import Tag

from .base_load_command import BaseLoadDataCommand


class Command(BaseLoadDataCommand):
    help = 'Загруска json данных об ингредиентах в базу данных.'
    file_name = 'tags'
    model = Tag
