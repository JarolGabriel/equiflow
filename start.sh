#!/bin/bash


python manage.py migrate --noinput

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Iniciando Celery Worker..."
    celery -A core worker --loglevel=info
elif [ "$SERVICE_TYPE" = "beat" ]; then
    echo "Iniciando Celery Beat..."
    celery -A core beat --loglevel=info
else
    echo "Iniciando Servidor Web (Daphne)..."
    daphne -b 0.0.0.0 -p 8000 core.asgi:application
fi