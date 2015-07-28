import os

# username on remote
ENV_USER = 'root'

# remote hosts
HOSTS = ( 
    '127.0.0.1',
    )

ALLOWED_HOSTS = HOSTS

# Django secret key
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# SECURITY WARNING: keep the secret key used in production secret!

########## SECRET CONFIGURATION
# SECURITY WARNING: keep the secret key used in production secret!
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "SuperSecretKey"
)
########## END SECRET CONFIGURATION

# Stripe secret keys
STRIPE_SECRET_KEY = 'sk_test_HJFprvoBQQcFpHMcJ4fcP4Nb'
STRIPE_PUBLIC_KEY = 'pk_test_wLynQ6aB7z7gx5vztfV37MVa'

TEST_STRIPE_SECRET_KEY = 'sk_test_HJFprvoBQQcFpHMcJ4fcP4Nb'
TEST_STRIPE_PUBLIC_KEY = 'pk_test_wLynQ6aB7z7gx5vztfV37MVa'