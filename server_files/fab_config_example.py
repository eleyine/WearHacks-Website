"""
This file must be copied and renamed to fab_config.py
It contains deployment-specific settings.
"""

########### DEPLOYMENT OPTIONS
DEFAULT_DEPLOY_TO='default'

# see wearhacks_website/settings/dev.py and 
# wearhacks_website/settings/prod.py

DEPLOYMENT_MODES = ('dev', 'prod')
DEFAULT_MODE='prod' 
DEFAULT_BRANCH='master'

# The following settings are used to manage different servers. 
# 
# For example, I use an 'alpha' server for personal testing, a 'beta' server to 
# show the team and a 'live' server for our official website.
# For each setting, please specify the corresponding private file which 
# contains security keys, passwords and other user-specific information.
# Private files must be located under wearhacks_website/settings/
#
# When it's necessary, fab will replace the server's private.py with the private
# file specified below. 
# 
# See:
#   - wearhacks_website/settings/__init__.py
#   - wearhacks_website/settings/private_settings_example.py

DEPLOYMENT_PRIVATE_FILES = {
    'default': 'server_private',
    # 'alpha': 'alpha_private',
    # 'beta': 'beta_private',
    # 'live': 'live_private'
}
DEPLOYMENT_HOSTS = {
    'default': ('127.0.0.1',), # change to your host e.g. 12.34.567.89
    # 'alpha': ('127.0.0.1',),
    # 'beta': ('127.0.0.1',),
    # 'live': ('127.0.0.1',)
}
########### END DEPLOYMENT OPTIONS