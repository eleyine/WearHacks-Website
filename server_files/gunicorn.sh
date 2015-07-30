description "Gunicorn daemon for Django project"
# Source for /etc/init/gunicorn.conf
# Be sure to change APP_NAME and PROJECT_NAME,  

start on (local-filesystems and net-device-up IFACE=eth0)
stop on runlevel [!12345]

# If the process quits unexpectadly trigger a respawn
respawn

setuid django
setgid django
chdir DJANGO_PROJECT_DIR

exec gunicorn \
    --name=DJANGO_PROJECT_NAME \
    --pythonpath=DJANGO_PROJECT_NAME \
    --bind=127.0.0.1:9000 \
    --config /etc/gunicorn.d/gunicorn.py \
DJANGO_APP_NAME.wsgi:application