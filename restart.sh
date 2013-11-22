#!/bin/sh

export DJANGO_SETTINGS_MODULE=settings

export ENV=prod

./manage.py collectstatic --noinput 

sudo service apache2 restart
