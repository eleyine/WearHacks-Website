from __future__ import absolute_import

from os.path import join, normpath
from os import environ

from .base import *

########## PRIVATE SETTINGS DO NOT MAKES THIS FILE PUBLIC
try:
    from settings.private import *
except ImportError:
    print 'ERROR: You must make a private.py file (see wearhacks_website/settings/private_example.py)'
    from settings.private_example import *
    sys.exit() # comment out this line if you want to use the example private settings
########## END PRIVATE SETTINGS DO NOT MAKES THIS PUBLIC

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

########## SECRET CONFIGURATION
# SECURITY WARNING: keep the secret key used in production secret!
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    TEST_SECRET_KEY # defined in private.py
)
########## END SECRET CONFIGURATION

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

########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
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

########## STRIPE

STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY",
    TEST_STRIPE_SECRET_KEY # defined in private.py
)
STRIPE_PUBLIC_KEY = os.environ.get(
    "STRIPE_PUBLIC_KEY",
    TEST_STRIPE_PUBLIC_KEY # defined in private.py
)
########## END STRIPE