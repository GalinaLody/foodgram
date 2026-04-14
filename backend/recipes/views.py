from django.http import Http404
from django.shortcuts import redirect

from .models import Recipe


def redirect_to_recipe_url(request, recipe_id):
    """При получении короткой ссылки рецепта перенаправляет пользователя
    на страницу рецепта."""
    if Recipe.objects.filter(id=recipe_id).exists():
        return redirect(f'/recipes/{recipe_id}')
    else:
        raise Http404('Рецепт не найден')
