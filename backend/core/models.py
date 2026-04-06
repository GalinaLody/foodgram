from django.db import models
from django.db.models.functions import Lower

from core.constants import SLICE_OUTPUT_STR_METHOD


class NameBaseModel(models.Model):
    """Абстрактный класс для поля name в моделях Tag и Ingredient."""

    class Meta:
        abstract = True
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                Lower('name'),
                name='%(app_label)s_%(class)s_unique_name',
                violation_error_message='Такой объект уже существует.'
            ),
        )

    def __str__(self):
        return self.name[:SLICE_OUTPUT_STR_METHOD]
