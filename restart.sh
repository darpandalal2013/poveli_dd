#!/bin/sh

export DJANGO_SETTINGS_MODULE=settings

./manage.py collectstatic --noinput 

sudo service apache2 restart
