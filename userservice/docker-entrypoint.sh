#!/bin/bash
set -euo pipefail

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Apply database migrations
if [ -v DEV_MODE ]; then
    echo "Apply database migrations in DEV_MODE"
    python manage.py makemigrations
    python manage.py migrate
fi
