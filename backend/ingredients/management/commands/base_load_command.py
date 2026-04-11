"""
Общий класс для менеджментов команд для загрузки тестовых данных из JSON-файлов
в базу данных проекта

Команда предназначена для первичного наполнения базы данных.

Загрузка выполняется через bulk_create(ignore_conflicts=True),
поэтому повторный запуск не создаёт дубликаты.
"""

import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class BaseLoadDataCommand(BaseCommand):
    def handle(self, *args, **kwargs):
        file_path = os.path.join(
            settings.BASE_DIR, 'data', f'{self.file_name}.json'
        )
        try:
            with open(file_path, encoding='utf-8') as data:
                objects = [self.model(**object) for object in json.load(data)]
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Загрузка данных для модели {self.model.__name__}'
                    )
                )
            count = self.model.objects.bulk_create(
                objects, ignore_conflicts=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Данные в количестве {len(count)} объектов '
                    f'для модели {self.model.__name__} загружены!'
                )
            )
        except FileNotFoundError:
            raise CommandError(f'Файл {self.file_name}.json не найден')
