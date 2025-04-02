#!/bin/sh
echo "Esperando o PostgreSQL ficar pronto..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL está pronto. Aplicando migrações..."

python manage.py makemigrations
python manage.py makemigrations tickets
python manage.py migrate users
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate admin
python manage.py migrate events
python manage.py migrate tickets
python manage.py migrate sessions
python manage.py migrate django_celery_beat

python manage.py migrate

echo "Iniciando Django..."
exec python manage.py runserver 0.0.0.0:8000
