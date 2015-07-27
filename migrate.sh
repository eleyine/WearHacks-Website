python manage.py sqlclear registration | python manage.py dbshell 
python manage.py makemigrations
python manage.py migrate
python manage.py syncdb
python manage.py generate_registrations 1 --reset
python manage.py runserver

