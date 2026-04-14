from datetime import date

from django.template.loader import render_to_string


def create_shopping_cart_text(ingredients, recipes):
    """Создает список покупок пользователя в текстовом формате."""
    return render_to_string(
        'shopping_cart.txt',
        {
            'date': date.today().strftime('%d.%m.%Y'),
            'ingredients': [
                {
                    'name': ingredient['ingredient__name'].capitalize(),
                    'unit': ingredient['ingredient__measurement_unit'],
                    'amount': ingredient['total_amount'],
                }
                for ingredient in ingredients
            ],
            'recipes': recipes,
        }
    )
