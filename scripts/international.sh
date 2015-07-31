#!/bin/bash

export PYTHONPATH="${PYTHONPATH}:`pwd`"
echo "Python path: ${PYTHONPATH}"
export DJANGO_SETTINGS_MODULE=wearhacks_website.settings
echo "Django settings module: ${DJANGO_SETTINGS_MODULE}"
echo $PATH

echo "Make messages in root dir `pwd`"
pwd
django-admin makemessages -x js --settings=wearhacks_website.settings
cd registration
mkdir -p locale

echo "Make messages in registration dir `pwd`"
django-admin makemessages -x js --settings=wearhacks_website.settings

cd ../static/javascripts
echo "Make messages in dir `pwd`"
django-admin makemessages -d djangojs --settings=wearhacks_website.settings

# cd ../..
# echo "Compile messages in dir `pwd`"
# django-admin compilemessages --settings=wearhacks_website.settings