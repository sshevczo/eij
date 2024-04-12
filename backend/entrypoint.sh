#!/bin/bash

# Импортируем переменные из файла .env
source .env

# Создаем миграции
python manage.py makemigrations --noinput

# Мигрируем базу данных
python manage.py migrate --noinput

# Собираем статические файлы
python manage.py collectstatic --noinput

# Меняем владельца статических файлов
chown -R 1000:1000 /usr/src/django_back/static

# Запускаем Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --timeout 120
