from datetime import date

from django.template.loader import render_to_string


def create_shopping_cart_text(ingredients, recipes):
    """Создает список покупок пользователя в текстовом формате."""
    return render_to_string(
        'shopping_cart.txt',
        {
            'date': date.today().strftime('%d.%m.%Y'),
            'ingredients': ingredients,
            'recipes': recipes,
        }
    )
