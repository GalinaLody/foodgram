## Описание проекта.

Foodgram - это проект в формате сайта рецептов с элементами соцальной сети, в которой пользователь может публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Backend проекта основан на Rest API. Frontend проекта использует React.

# api_foodgram
api foodgram

## Технологический стек проекта.
- Python 3.12  
- Django  
- Django REST Framework (DRF)
- POSTGRESQL 
- REST API 

## Установка API Foodgram.

Необходимо клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:GalinaLody/foodgram.git
```
```
cd fodgram
```
Cоздать и активировать виртуальное окружение:

```
python -m venv env
```
* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
## Примеры запросов к API Foodgram.

Запросы к API Foodgram могут быть отправлены на следующие эндпоинты:
* http://127.0.0.1:8000/users/
* http://127.0.0.1:8000/api/users/{id}/
* http://127.0.0.1:8000/api/users/me/
* http://127.0.0.1:8000/api/users/me/avatar/
* http://127.0.0.1:8000/api/users/set_password/
* http://127.0.0.1:8000/api/auth/token/login/
* http://127.0.0.1:8000/api/auth/token/logout/
* http://127.0.0.1:8000/api/tags/
* http://127.0.0.1:8000/api/tags/{id}/
* http://127.0.0.1:8000/api/recipes/
* http://127.0.0.1:8000/api/recipes/{id}/
* http://127.0.0.1:8000/api/recipes/{id}/get-link/
* http://127.0.0.1:8000/api/recipes/download_shopping_cart/
* http://127.0.0.1:8000/api/recipes/{id}/shopping_cart/
* http://127.0.0.1:8000/api/recipes/{id}/favorite/
* http://127.0.0.1:8000/api/users/subscriptions/
* http://127.0.0.1:8000/api/users/{id}/subscribe/
* http://127.0.0.1:8000/api/ingredients/
* http://127.0.0.1:8000/api/ingredients/{id}/

Для просмотра рецептов на главной странице, отдельных страниц рецепта, страниц пользователей регистрации не требуется. Для осуществления иных действий, например, создание, изменение, рецептов, списка покупок, подписок, избранного требуется аутентификация пользователя.

Для регистрации пользователя необходимо направить запрос на эндпоинт http://127.0.0.1:8000/users/.

Пример запроса:
```
{
"email": "vpupkin@yandex.ru",
"username": "vasya.pupkin",
"first_name": "Вася",
"last_name": "Иванов",
"password": "Qwerty123"
}
```
Получение токена  осуществляется пользователем путем напарвления запроса с email и паролем на эндпоинт http://127.0.0.1:8000/api/auth/token/login/.

Пример запроса:
```
{
"password": "string",
"email": "string"
}
```

Для содания рецепта необходимо направит запрос на эндпоинт http://127.0.0.1:8000/api/recipes/

Пример запроса:
```
{

"ingredients": [
{
"id": 1123,
"amount": 10
}
],
"tags": [
1,
2
],
"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
"name": "string",
"text": "string",
"cooking_time": 1
}
```

Для добавления рецепта в список покупок необходимо направит запрос на эндпоинт http://127.0.0.1:8000/api/recipes/{id}/shopping_cart/

Пример запроса:
```
{

"id": 0,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.png",
"cooking_time": 1
}
```


Автор Галина Лодыгина, Данил Демура
email: Zolotova-87-gali@yandex.ru


