#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="misha").exists():
    User.objects.create_superuser("misha", "mykhailo.polietaiev@evowill.com", "misha823")
    print("Superuser 'misha' created successfully.")
else:
    print("Superuser 'misha' already exists.")
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn myblog.wsgi:application --bind 0.0.0.0:8000
