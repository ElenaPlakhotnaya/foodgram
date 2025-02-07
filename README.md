## 1. Описание проекта Foodgram
«Foodgram» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Зарегистрированным пользователям также будет доступен сервис «Список покупок». 
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## 2. Стек проекта (список технологий):

Язык программирования: *Python*

Фреймворк: *Django*

База данных: *PostgreSQL*

API: *Django Rest Framework*

Системы контроля версий: *Git*

Инструменты разработки: *VSCode*

Управление зависимостями: *pip, requirements.txt*

Сервер: *Nginx*

WSGI-сервер: *Gunicorn*

Контейнеризация: *Docker*

Аутентификационный бэкенд: *Djoser*

## 3. Как запустить проект: 

Клонировать репозиторий и перейти в него в командной строке 
 
### Cоздать и активировать виртуальное окружение: 

Windows 

``` python -m venv venv ``` 
``` source venv/Scripts/activate ``` 

Linux/macOS

``` python3 -m venv venv ``` 
``` source venv/bin/activate ``` 

### Обновить PIP 
 
Windows 

``` python -m pip install --upgrade pip ``` 

Linux/macOS 

``` python3 -m pip install --upgrade pip ``` 
 
### Установить зависимости из файла requirements.txt: 
 
``` pip install -r requirements.txt ``` 
 

### Запустить проект с помощью Docker: 

На сервере создать директорию foodgram и перейти в нее.

```mkdir foodgram/```
```cd foodgram```

Скопируйте файл docker-compose.production.yml из текущего репозитория в корневую папку проекта foodgram/
В корневой папке проекта foodgram/ создайте файл .env и заполните его согласно примеру:
```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db
DB_HOST=db
DB_PORT=5432
SECRET_KEY = *key*
DEBUG = True
ALLOWED_HOSTS = 127.0.0.1,localhost,вашдомен
```
Выполните *git push*
Создайте администратора сайта
```sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser```

## 4. Ссылка на документацию:
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

## 5. Автор проекта:

Плахотная Елена 
