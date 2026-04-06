"""
Менеджмент команд для загрузки тестовых данных из CSV-файлов
в базу данных проекта

Команда предназначена для первичного наполнения базы данных
ингредиентами и тегами.

Использование:
    python manage.py load_data

Ожидаемые файлы:
    ingredients.csv
    tags.csv

Загрузка выполняется через bulk_create(ignore_conflicts=True),
поэтому повторный запуск не создаёт дубликаты.
"""

import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from ingredients.models import Ingredient
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загруска csv данных об ингредиентах и тегах в базу данных.'

    def handle(self, *args, **kwargs):
        name_models = {
            'ingredients': Ingredient,
            'tags': Tag,
        }
        for name, model in name_models.items():
            file_path = os.path.join(
                settings.BASE_DIR, 'data', f'{name}.csv'
            )
            with open(file_path, encoding='utf-8') as data:
                objects = []
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Загрузка данных для модели {model.__name__}'
                    )
                )
                for row in csv.DictReader(data):
                    fields = {}
                    for key, value in row.items():
                        fields[key] = value
                    objects.append(model(**fields))
                model.objects.bulk_create(objects, ignore_conflicts=True)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Данные для модели {model.__name__} загружены!'
                    )
                )
