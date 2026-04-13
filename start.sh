#!/bin/bash

set -e

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Daphne (ASGI) on port $PORT..."
exec daphne -b 0.0.0.0 -p $PORT core.asgi:application