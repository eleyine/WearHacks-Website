import os

# This file must be copied and renamed to private.py
# It contains sensitive / deployment-specific settings
# Do not make it public!

# Username on remote
ENV_USER = 'root'

# Remote hosts
HOSTS = ( 
    'YourHostIP', # e.g. '45.55.216.44'
    )

ALLOWED_HOSTS = (
    '.example.com',  # Allow domain and subdomains
    )

########## SECRET CONFIGURATION
# SECURITY WARNING: keep the secret key used in production secret!
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "SuperSecretKey"
)
########## END SECRET CONFIGURATION

########## STRIPE
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY',
    'sk_provided_by_stripe')
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY',
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
