apt-get install git
apt-get-install npm
sudo npm install -g bower
sudo npm install -g less
ln -s /usr/bin/nodejs /usr/bin/node

cd /home/django/
mv django_project old_django_project
git clone https://github.com/eleyine/WearHacks-Website.git django_project
chown -R django:django /home/django/djangoapptoscana/djangoapptoscana/static

export DJANGO_SETTINGS_MODULE=wearhacks_website.settings.local
export SECRET_KEY=mysecretkey

pip install -r requirements.txt
bower install --allow-root

service gunicorn restart

python manage.py makemigrations
python manage.py migrate
python manage.py runserver

