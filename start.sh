#!/bin/bash

# 1. Preparar la base de datos
echo "Ejecutando migraciones..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 2. Iniciar Celery Worker en segundo plano
echo "Iniciando Celery Worker..."
celery -A core worker --loglevel=info --concurrency=1 &

echo "Creando superusuario..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='tu_email@ejemplo.com').exists() or User.objects.create_superuser('tu_email@ejemplo.com', 'tu_password_segura')"

echo "Cargando activos semilla (Assets)..."
python manage.py seed_assets

# 3. Iniciar Celery Beat en segundo plano
echo "Iniciando Celery Beat..."
celery -A core beat --loglevel=info &

# 4. Iniciar el servidor Web (este se queda al frente)
echo "Iniciando Servidor Web..."
daphne -b 0.0.0.0 -p 8000 core.asgi:application