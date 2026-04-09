## Описание проекта.

Foodgram - это проект в формате сайта рецептов с элементами соцальной сети, в которой пользователь может публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Backend проекта основан на Rest API. Frontend проекта использует React.


## Технологический стек проекта.
- Python 3.12  
- Django  
- Django REST Framework (DRF)
- POSTGRESQL 
- REST API 
- Gunicorn 
- Nginx 
- Docker 
- Docker Compose

## Как запустить проект.

Необходимо клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:GalinaLody/foodgram.git

cd fodgram
```
Cоздать переменные окружения .env на основании .env.example:

```
cp .env.example .env
```

Собирать образы и запустить контейнеры:

```
docker compose up --build -d
```

Выполнить миграции:

```
docker compose exec backend python manage.py migrate
```

Собрать статику:

```
docker compose exec backend python manage.py collectstatic

docker compose exec backend cp -r /app collected_static/. /backend_static/static/
```

Загрузить базу ингредиентов и тегов:

```
docker compose exec backend python manage.py load_data
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
## Деплой на сервер.

Прописать GitHub Secrets:
 - SSH_KEY
 - USER
 - HOST
 - DOCKER_USERNAME
 - DOCKER_PASSWORD
 - TELEGRAM_ID
 - TELEGRAM_TOKEN

Создать .env на сервере.
Скопировать на сервер файл docker-compose.yml. Из директории с
файлом docker-compose.yml выполнить команду:

```
scp -i path_to SSH/SSH_name docker-compose.yml username@server_ip:/home/username/docker-compose.yml
```
Загрузить на GitHub в главную ветку:

```
git pull
```
При пуше в main запускается workflows, проверяется линтинг
собираются Docker-образы, деплоится на сервер по SSH

## Доступы.

1.[Сервер](https://foodgram.serveirc.com/);
2.[Админка](https://foodgram.serveirc.com/admin/);
[API-документация]()


[Автор: Галина Лодыгина](Zolotova-87-gali@yandex.ru)


