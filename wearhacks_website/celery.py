from __future__ import absolute_import
import os
from celery import Celery
from datetime import timedelta

# set the default Django settings module for the 'celery' program.
# os.environ.setdefault('APP_ENV', 'prod')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wearhacks_website.settings')

from django.conf import settings

app = Celery('wearhacks_website',
             broker=settings.BROKER_URL,
             backend='amqp://',
             # include=['wearhacks_website.tasks'],
             )

# Optional configuration, see the application user guide.
# A built-in periodic task will delete the results after this time 
# app.conf.update(
#     CELERY_TASK_RESULT_EXPIRES=3600, # 1hour
# )

# Configure celery
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    CELERY_CACHE_BACKEND='djcelery.backends.cache:CacheBackend',
    CELERYBEAT_SCHEDULE = {
        'backup-every-30-seconds': {
            'task': 'tasks.registration.dropbox_backup',
            'schedule': timedelta(seconds=30)
        },
    },
    CELERYD_CHDIR = settings.SITE_ROOT
)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

if __name__ == '__main__':
    app.start()