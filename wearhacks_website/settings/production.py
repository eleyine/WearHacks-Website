"""Production settings and globals."""

from __future__ import absolute_import

from os import environ
import sys

from .base import *

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

########## PRIVATE SETTINGS DO NOT MAKES THIS FILE PUBLIC
try:
    from settings import private
except ImportError:
    print 'ERROR: You must make a private.py file (see wearhacks_website/settings/private_example.py)'
    from settings import private_example as private
    sys.exit() # comment out this line if you want to use the example private settings
########## END PRIVATE SETTINGS DO NOT MAKES THIS PUBLIC

########## SECRET KEY CONFIGURATION
# SECURITY WARNING: keep the secret key used in production secret!
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    private.PROD_SECRET_KEY # defined in private.py
)
########## END SECRET KEY CONFIGURATION

########## HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production
ALLOWED_HOSTS = []
########## END HOST CONFIGURATION

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'your_email@example.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER
########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', private.DB_NAME),
        'USER': os.environ.get('DB_USER', private.DB_USER),
        'PASSWORD': os.environ.get('DB_PASS', private.DB_PASS),
        'HOST': os.environ.get('DB_HOST', private.DB_HOST),
        'PORT': os.environ.get('DB_PORT', private.DB_PORT),
    }
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
# Need to change to more efficient cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION

########## STRIPE

STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY",
    private.STRIPE_SECRET_KEY # defined in private.py
)
STRIPE_PUBLIC_KEY = os.environ.get(
    "STRIPE_PUBLIC_KEY",
    private.STRIPE_PUBLIC_KEY # defined in private.py
)
########## END STRIPE