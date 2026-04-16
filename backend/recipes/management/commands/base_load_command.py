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
    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            nargs='?',
            type=str,
            default=os.path.join(
                settings.BASE_DIR, 'data', f'{self.file_name}.json'
            )
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with open(file_path, encoding='utf-8') as data:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Загрузка данных для модели {self.model.__name__}'
                    )
                )
                created = self.model.objects.bulk_create(
                    (self.model(**item_data) for item_data in json.load(data)),
                    ignore_conflicts=True
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Загрузка данных из файла {file_path} '
                    f'в модель {self.model.__name__} завершена. '
                    f'Успешно добавленных объектов: {len(created)}.'
                )
            )
        except Exception as error:
            raise CommandError(
                f'Ошибка загрузки файла {file_path}: {error}'
            )
