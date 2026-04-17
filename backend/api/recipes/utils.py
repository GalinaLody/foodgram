from datetime import date

from django.template.loader import render_to_string

MONTHS_RU = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
    5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
    9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}


def create_shopping_cart_text(ingredients, recipes):
    """Создает список покупок пользователя в текстовом формате."""
    return render_to_string(
        'shopping_cart.txt',
        {
            'date': (
                f'{date.today().day} '
                f'{MONTHS_RU[date.today().month]} {date.today().year}'
            ),
            'ingredients': ingredients,
            'recipes': recipes,
        }
    )
