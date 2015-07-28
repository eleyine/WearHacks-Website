# username on remote
ENV_USER = 'root'

# remote hosts
HOSTS = ( 
    '162.243.185.49',
    # 'wearhacks.eleyine.com',
    '45.55.84.109', # FabTest
    # '45.55.216.44', # WearHacks
    )

ALLOWED_HOSTS = (
    '.eleyine.com',  # Allow domain and subdomains
    )

# Django secret key
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
TEST_SECRET_KEY = 'YourSecretKey'
# SECURITY WARNING: keep the secret key used in production secret!
PROD_SECRET_KEY = 'u-i^q400q!_q)93w+mt(8!9%h64_*lntc%1lo5&kfdzopf2ns!'

# Postgres user settings for production
DB_NAME = 'django'
DB_USER = 'django'
DB_PASS = 'BsSMA2QZV0'
DB_HOST = 'localhost'
DB_PORT = 5432

# Stripe secret keys
STRIPE_SECRET_KEY = 'sk_test_HJFprvoBQQcFpHMcJ4fcP4Nb'
STRIPE_PUBLIC_KEY = 'pk_test_wLynQ6aB7z7gx5vztfV37MVa'

TEST_STRIPE_SECRET_KEY = 'sk_test_HJFprvoBQQcFpHMcJ4fcP4Nb'
TEST_STRIPE_PUBLIC_KEY = 'pk_test_wLynQ6aB7z7gx5vztfV37MVa'

# Useful when managing different servers. For example, you can have a 
# dev_private.py and prod_private.py with different api keys and db credentials
# which will override settings in private.py
PRIVATE_FILENAME = 'private.py'