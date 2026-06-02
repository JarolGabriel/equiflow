#!/bin/bash

# 1. Database and Static Files
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# 2. Start Celery Worker in background
echo "Starting Celery Worker..."
celery -A core worker --loglevel=info --concurrency=1 &

# 3. Start the Web Server
echo "Starting Daphne on port $PORT..."
# exec daphne -b 0.0.0.0 -p $PORT core.asgi:application
exec daphne -b 0.0.0.0 -p ${PORT:-8000} core.asgi:application