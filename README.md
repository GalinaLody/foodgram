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

## Начало работы с проектом.


Необходимо клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:GalinaLody/foodgram.git

cd foodgram
```
Cоздать переменные окружения .env на основании .env.example:

```
cp .env.example .env
```
## Как запустить проект локально.

Работа с backend.

Перйти в директорю backend, создать и активировать виртуальное окружение:

```
cd backend

python -m venv venv

source venv/Scripts/activate
```
Обновить pip, установить зависимости backend, применить миграции, создать суперпользователя:

```
pip install --upgrade pip

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser
```

Запустить веб-сервер разработки:

```
python manage.py runserver 0:8000
```

Работа с frontend 

Если не установлено установить Node.js с nodejs.org

Открыть новый терминал, перейти в директорию frontend и установить зависимости:

```
cd ../frontend

npm i
```

Запустить frontend-приложение:

```
npm run start
```

После запуска открыть http://localhost:3000 в браузере.


## Как запустить проект локально в контейнерах.

Ввыполнить команды в директории foodgram(по месту нахождения файла docker-compose.local.yml)

Cоздать переменные окружения .env.local на основании .env.example:

```
cp .env.example .env
```

Собрать образы и запустить контейнеры:

```
docker compose -f docker-compose.common.yml -f docker-compose.local.yml up --build -d
```

Выполнить миграции:

```
docker compose -f docker-compose.common.yml -f docker-compose.local.yml exec backend python manage.py migrate
```

Собрать статику:

```
docker compose -f docker-compose.common.yml -f docker-compose.local.yml exec backend python manage.py collectstatic

docker compose -f docker-compose.common.yml -f docker-compose.local.yml exec backend cp -r /app collected_static/. /backend_static/static/
```

Загрузить базу ингредиентов и тегов:

```
docker compose -f docker-compose.common.yml -f docker-compose.local.yml exec backend python manage.py load_tags

docker compose -f docker-compose.common.yml -f docker-compose.local.yml exec backend python manage.py load_ingredients
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
Скопировать на сервер в одну директорию файлы docker-compose.common.yml и docker-compose.product.yml
Из директории с файлами docker-compose.common.yml и docker-compose.product.yml выполнить команду:

```
scp -i path_to SSH/SSH_name docker-compose.common.yml docker-compose.product.yml username@server_ip:/home/username/ docker-compose.common.yml docker-compose.product.yml
```
Загрузить на GitHub в главную ветку:

```
git pull
```
При пуше в main запускается workflows, проверяется линтинг
собираются Docker-образы, деплоится на сервер по SSH

## Доступы.

[Сервер](https://foodgram.serveirc.com/);
[Админка](https://foodgram.serveirc.com/admin/);
[API-документация](https://foodgram.serveirc.com/api/docs/).


[Автор: Галина Лодыгина](Zolotova-87-gali@yandex.ru)
