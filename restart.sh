#!/bin/sh

export DJANGO_SETTINGS_MODULE=settings

find . -name "*.pyc" -delete

./manage.py migrate

./manage.py collectstatic --noinput 

sudo service apache2 restart
