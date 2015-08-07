from __future__ import absolute_import

from os.path import join, normpath
from os import environ

from wearhacks_website.settings.common import DJANGO_ROOT

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = environ.get('COMPRESS_ENABLED', not DEBUG)
########## END DEBUG CONFIGURATION

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + join(DJANGO_ROOT, 'db.sqlite3')
    )
}
########## END DATABASE CONFIGURATION

# Allow all host headers
ALLOWED_HOSTS = ['*']

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION

########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION

########## CELERY
# run celery task synchronous
CELERY_ALWAYS_EAGER = True
########## END CELERY

########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
DJANGO_APPS = (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR': False,
    'INSERT_BEFORE': '<!-- Debug Toolbar -->',
}

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION