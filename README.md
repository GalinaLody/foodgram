[![Main Foodgram workflow](https://github.com/GalinaLody/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/GalinaLody/foodgram/actions/workflows/main.yml)
## Описание проекта.

Foodgram - это проект в формате сайта рецептов с элементами соцальной сети, в которой пользователь может публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Backend проекта основан на Rest API. Frontend проекта использует React.


## Технологический стек проекта.
- Python 3.12  
- Django  
- Django REST Framework (DRF)
- POSTGRESQL 
- SQLite 
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
Обновить pip, установить зависимости backend, применить миграции, создать суперпользователя, загрузить данные в базу:

```
pip install --upgrade pip

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py load_ingredients

python manage.py load_tags
```

Запустить веб-сервер разработки:

```
python manage.py runserver 0:8000
```

Работа с frontend 

Требуется Node.js с nodejs.org

Открыть новый терминал, перейти в директорию frontend и установить зависимости:

```
cd ../frontend

npm i
```

Запустить frontend-приложение:

```
npm run start
```

После запуска открыть [сервер](http://localhost:3000) в браузере.
Доступ к [Админке](http://localhost:3000/admin/).

## Доступ к Api-документации.

Открыть Api-документацию можно с использованием онлаин-редактора [Swagger](https://editor.swagger.io/)

путем загрузки файла foodgram/docs/openapi-schema.yml

## Как запустить проект локально в контейнерах.

Необходимо клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:GalinaLody/foodgram.git

cd foodgram

```


Ввыполнить команды в директории foodgram(по месту нахождения файла docker-compose.local.yml)



Cоздать переменные окружения .env.local на основании .env.example:

```
cp .env.example .env.local
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

## Деплой на сервер.

Необходимо клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:GalinaLody/foodgram.git

cd foodgram

```

Создать .env на сервере.

Прописать GitHub Secrets:
 - SSH_KEY
 - USER
 - HOST
 - DOCKER_USERNAME
 - DOCKER_PASSWORD
 - TELEGRAM_ID
 - TELEGRAM_TOKEN


## Доступы.

[Сервер](https://foodgram.serveirc.com/);
[Админка](https://foodgram.serveirc.com/admin/);
[API-документация](https://foodgram.serveirc.com/api/docs/).

## Автор.

[Галина Лодыгина](Zolotova-87-gali@yandex.ru)
