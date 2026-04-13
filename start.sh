#!/bin/bash


python manage.py migrate


celery -A core worker --loglevel=info &


celery -A core beat --loglevel=info &


daphne -b 0.0.0.0 -p $PORT core.asgi:application