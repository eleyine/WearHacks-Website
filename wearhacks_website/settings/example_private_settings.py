"""
This file must be copied and renamed to private.py
It contains sensitive / deployment-specific settings
Do not make it public!
"""
from __future__ import absolute_import
import os
from .common import SITE_NAME

# Username on remote
ENV_USER = 'root'

# Remote hosts
# The first item will be used as the url domain when making 
# absolute urls (e.g. in the email confirmation)
HOSTS = ( 
    'YourHostIP', # e.g. '45.55.216.44'
    )

ALLOWED_HOSTS = (
    '.example.com',  # Allow domain and subdomains
    '.example.com.', 
    )

SITE_NAME = 'Example Website'

########## SECRET CONFIGURATION
# SECURITY WARNING: keep the secret key used in production secret!
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "SuperSecretKey"
)
########## END SECRET CONFIGURATION

########## STRIPE
LIVE_STRIPE_SECRET_KEY = os.environ.get('LIVE_STRIPE_SECRET_KEY',
    'sk_provided_by_stripe')
LIVE_STRIPE_PUBLIC_KEY = os.environ.get('LIVE_STRIPE_PUBLIC_KEY',
    'pk_provided_by_stripe')

TEST_STRIPE_SECRET_KEY = os.environ.get('TEST_STRIPE_SECRET_KEY',
    'sk_test_provided_by_stripe')
TEST_STRIPE_PUBLIC_KEY = os.environ.get('TEST_STRIPE_PUBLIC_KEY',
    'pk_test_provided_by_stripe')

# Once your site is live, change this to True
IS_STRIPE_LIVE = False
########## END STRIPE

# Comment out if you want a postgresql database backend
# Otherwise, the default database backend is sqlite3
# 
# ########## POSTGRES SETTINGS
# DB_NAME = 'django'
# DB_USER = 'django'
# DB_PASS = 'pass'
# DB_HOST = 'localhost'
# DB_PORT = ''
# ########## END POSTGRES SETTINGS

# ########## DATABASE CONFIGURATION
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.environ.get('DB_NAME', DB_NAME),
#         'USER': os.environ.get('DB_USER', DB_USER),
#         'PASSWORD': os.environ.get('DB_PASS', DB_PASS),
#         'HOST': os.environ.get('DB_HOST', DB_HOST),
#         'PORT': os.environ.get('DB_PORT', DB_PORT),
#     }
# }
# ########## END DATABASE CONFIGURATION

########## EMAIL / MANDRILL
MANDRILL_API_KEY = "your_mandrill_api_key"
EMAIL_BACKEND = 'djrill.mail.backends.djrill.DjrillBackend' 

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.mandrillapp.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', MANDRILL_API_KEY)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'user@example.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
########## END EMAIL / MANDRILL
