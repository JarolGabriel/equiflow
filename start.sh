#!/bin/bash

# 1. Preparar la base de datos
echo "Ejecutando migraciones..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 2. Iniciar Celery Worker en segundo plano
echo "Iniciando Celery Worker..."
celery -A core worker --loglevel=info --concurrency=1 &

echo "Poblando base de datos con assets iniciales..."
python manage.py seed_assets

echo "Revisando superusuario..."
python manage.py shell -c "from apps.users.models import User; User.objects.filter(email='flex.amazon2025@gmail.com').exists() or User.objects.create_superuser('flex.amazon2025@gmail.com', '123456789')"


# 4. Iniciar el servidor Web (este se queda al frente)
echo "Iniciando Servidor Web..."
daphne -b 0.0.0.0 -p 8000 core.asgi:application