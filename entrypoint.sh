#!/bin/bash
set -e

echo "=== INVENTORY SYSTEM STARTUP ==="
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL started"

echo "Creating cache table..."
python manage.py createcachetable || true

# Migrar apps core en orden
echo "Migrating core apps..."
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate users
python manage.py migrate admin
python manage.py migrate sessions

# Hacer migraciones para todas las apps
echo "Making migrations for all apps..."
python manage.py makemigrations products || true
python manage.py makemigrations warehouses || true
python manage.py makemigrations suppliers || true
python manage.py makemigrations inventory || true
python manage.py makemigrations movements || true
python manage.py makemigrations audit || true
python manage.py makemigrations reports || true

# Migrar todas las apps
echo "Migrating all apps..."
python manage.py migrate

echo "Creating initial data..."
python manage.py create_initial_data || echo "Initial data already exists"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000