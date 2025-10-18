#!/bin/bash

# Wait for MySQL to be ready
echo "Waiting for MySQL database..."
while ! mysqladmin ping -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" --silent; do
    echo "MySQL is unavailable - sleeping"
    sleep 2
done

echo "MySQL is up - executing migrations"
python manage.py migrate

echo "Starting server"
python manage.py runserver 0.0.0.0:8000