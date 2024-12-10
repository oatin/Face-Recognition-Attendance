#!/bin/sh

python manage.py makemigrations members
python manage.py migrate members
python manage.py makemigrations
python manage.py migrate

exec "$@"