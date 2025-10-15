#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python manage.py shell < create_superuser.py

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn myblog.wsgi:application --bind 0.0.0.0:8000
