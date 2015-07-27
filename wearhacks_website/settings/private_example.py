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

# Django secret key
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
TEST_SECRET_KEY = 'YourSecretKey'
# SECURITY WARNING: keep the secret key used in production secret!
PROD_SECRET_KEY = 'YourSuperSecretKey'

# Postgres user settings for production
DB_NAME = 'django'
DB_USER = 'django'
DB_PASS = 'pass'
DB_PORT = 5432

# Stripe secret keys
STRIPE_SECRET_KEY = 'sk_provided_by_stripe'
STRIPE_PUBLIC_KEY = 'pk_provided_by_stripe'

TEST_STRIPE_SECRET_KEY = 'sk_test_provided_by_stripe'
TEST_STRIPE_PUBLIC_KEY = 'pk_test_provided_by_stripe'