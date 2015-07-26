# This file must be copied and renamed to private.py
# It contains sensitive / deployment-specific settings
# Do not make it public!

# Username on remote
ENV_USER = 'root'

# Remote hosts
HOSTS = ( 
    'YourHostIP', # e.g. '45.55.216.44'
    )

# Django secret key
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = 'YourSecretKey'

# Postgres databse user settings for production
DB_USER = 'django'
DB_PASS = 'YourDatabasePassword'


