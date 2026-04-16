from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from .models import Recipe


def redirect_to_recipe_url(request, recipe_id):
    """При получении короткой ссылки рецепта перенаправляет пользователя
    на страницу рецепта."""
    if Recipe.objects.filter(id=recipe_id).exists():
        return redirect(f'/recipes/{recipe_id}')
    raise ValidationError(f'Рецепт с id={recipe_id} не найден')
