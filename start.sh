#!/bin/bash


set -e

echo "Running migrations..."
python manage.py migrate

echo "Starting Celery Worker..."

celery -A core worker --loglevel=info &

echo "Starting Celery Beat..."
celery -A core beat --loglevel=info &

echo "Starting Daphne (ASGI)..."

exec daphne -b 0.0.0.0 -p $PORT core.asgi:application