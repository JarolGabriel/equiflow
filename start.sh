#!/bin/bash

# 1. Preparar la base de datos
echo "Ejecutando migraciones..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 2. Iniciar Celery Worker en segundo plano
echo "Iniciando Celery Worker..."
celery -A core worker --loglevel=info --concurrency=1 &

# 3. Iniciar Celery Beat en segundo plano
echo "Iniciando Celery Beat..."
celery -A core beat --loglevel=info &

# 4. Iniciar el servidor Web (este se queda al frente)
echo "Iniciando Servidor Web..."
daphne -b 0.0.0.0 -p 8000 core.asgi:application