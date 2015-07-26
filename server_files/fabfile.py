"""
Script to perform common operations on remote server from local machine.

Prerequisites:
    pip install fabric
    Create DigitalOcean droplet with Django installation
    Copy private_example.py to private.py and edit in your settings

Usage:
    fab setup
    ---------
        Installs git and package managers (npm, bower)
        Modifies nginx and gunicorn configs to match our directory tree
        Clones github directory and installs python + bower requirements
        Add correct permission to static folder

    fab reboot:mode=prod
    ---------
        (Setup step assumed to be completed.)
        Pull changes from master repo
        Migrate database
        Restart nginx and gunicorn
        Run project using production settings (see wearhacks_website/settings/prod.py)

    fab reboot:mode=dev
    ---------
        (Setup step assumed to be completed.)
        Pull changes from master repo
        Migrate database
        Restart nginx and stop gunicorn
        Run on localhost:9000
        Run project using dev settings (see wearhacks_website/settings/local.py)

    fab get_logs
    ---------
        Copy nginx and gunicorn log files from remote to logs/ directory
"""

from fabric.api import *
from fabric.contrib.console import confirm
from fabric.context_managers import shell_env
import tempfile, os, sys

from private_example import *

if not os.path.exists('private.py'):
    print 'ERROR: You must make a private.py file (see server_files/private_example.py)'
    sys.exit() # comment out this line if you want to use the example private settings
else:
    from private import *

########### DJANGO SETTINGS
DEFAULT_MODE = 'dev' # or 'prod'
DEV_DJANGO_SETTINGS_MODULE = 'wearhacks_website.settings.local'
PROD_DJANGO_SETTINGS_MODULE = 'wearhacks_website.settings.production'
########### END DJANGO SETTINGS

########### PROMPT SETTINGS
AUTO_ANSWER_PROMPTS = True  
if AUTO_ANSWER_PROMPTS:
    prompts = {
        'Do you want to continue [Y/n]? ': 'Y',
        '? May bower anonymously report usage statistics to improve the tool over time? (Y/n)': 'Y'
        }
else:
    prompts = {}
########### END PROMPT SETTINGS

########### PATH AND PROJECT NAME CONFIGURATION
# Should not change if you do not modify this GitHub project
GITHUB_PROJECT = 'https://github.com/eleyine/WearHacks-Website.git'
DJANGO_PROJECT_DIR = '/home/django'
DJANGO_PROJECT_NAME = 'WearHacks-Website'
DJANGO_APP_NAME = 'wearhacks_website'
DJANGO_PROJECT_PATH = os.path.join(DJANGO_PROJECT_DIR, DJANGO_PROJECT_NAME)
########### END PATH AND PROJECT NAME CONFIGURATION

########### ENV VARIABLES
env.user = ENV_USER
env.hosts = HOSTS
########### END ENV VARIABLES

def write_file(local_path, remote_path, options):
    with open(local_path) as f:
        content = f.read()

    for option_name, option_value in options.iteritems():
        content = content.replace(option_name, option_value)

    #  tmp = tempfile.TemporaryFile()
    TMP_PATH = 'tmp.txt'
    with open(TMP_PATH, 'w') as tmp:
        tmp.write(content)

    print 'Overwriting %s' % (remote_path)
    put(TMP_PATH, remote_path)

def setup():
    with settings(warn_only=True):
        with settings(prompts=prompts):
            print 'Installing git...'
            run('apt-get install git')

            print 'Installing npm...'
            run('apt-get install npm')

        if not os.path.isfile('/usr/bin/node'):
            run('ln -s /usr/bin/nodejs /usr/bin/node')

        NPM_PACKAGES = ['bower', 'less']
        with settings(prompts=prompts):
            for package in NPM_PACKAGES:
                output = run(package)
                if 'command not found' in output:
                    print 'Installing %s as root...' % (package)
                    sudo('npm install -g %s' % (package))
                else:
                    print 'Updating %s as root...' % (package)
                    sudo('npm update -g %s' % (package))

        print 'Making django project directory at %s...' % (DJANGO_PROJECT_DIR)
        run('mkdir -p %s' % (DJANGO_PROJECT_DIR))

        print 'Modifying nginx config'
        write_file('nginx.sh', '/etc/nginx/sites-enabled/django',
            {
                'DJANGO_PROJECT_PATH': DJANGO_PROJECT_PATH
            })

        print 'Modifying gunicorn config'
        write_file('gunicorn.sh', '/etc/init/gunicorn.conf',
            {
                'DJANGO_PROJECT_DIR': DJANGO_PROJECT_DIR,
                'DJANGO_PROJECT_NAME': DJANGO_PROJECT_NAME,
                'DJANGO_APP_NAME': DJANGO_APP_NAME
            })

        if not os.path.exists(DJANGO_PROJECT_PATH):
            with cd(DJANGO_PROJECT_DIR):
                print 'Cloning Github Project into %s...' % (DJANGO_PROJECT_NAME)
                run('git clone %s %s' % (GITHUB_PROJECT, DJANGO_PROJECT_NAME)) 

        with cd(DJANGO_PROJECT_PATH):
            run('git pull origin master')
            print 'Installing python requirements..'
            run('pip install -r requirements.txt')
            
            print 'Installing bower requirements..'
            run('bower install --allow-root')

            # setup proper permissions
            sudo('chown -R django:django %s' % (os.path.join(DJANGO_PROJECT_PATH, 'static')))

def migrate(mode='prod'):

    print 'Migrating database'

    if mode == 'dev':
        DJANGO_SETTINGS_MODULE = DEV_DJANGO_SETTINGS_MODULE
    elif mode == 'prod':
        DJANGO_SETTINGS_MODULE = PROD_DJANGO_SETTINGS_MODULE
    else:
        print 'Invalid mode %s' % (mode)

    with shell_env(DJANGO_SETTINGS_MODULE=DJANGO_SETTINGS_MODULE, 
        SECRET_KEY=SECRET_KEY, DB_PASS=DB_PASS, DB_USER=DB_USER):
        with cd(DJANGO_PROJECT_PATH):
            run('python manage.py makemigrations')
            run('python manage.py migrate')

def pull_changes():
    with cd(DJANGO_PROJECT_PATH):
        print 'Pulling changes from master repo'
        run('git pull origin master')

def reboot(mode='prod'):

    with cd(DJANGO_PROJECT_PATH):
        print 'Pulling changes from master repo'
        run('git pull origin master')

        migrate(mode=mode)

        if mode == 'prod':
            print 'Restarting nginx'
            sudo('nginx -t')
            sudo('service nginx reload')

            print 'Restarting gunicorn'
            run('service gunicorn restart')

        elif mode == 'dev':
            print 'Restarting nginx'
            sudo('nginx -t')
            sudo('service nginx reload')

            print 'Stopping gunicorn' 
            try:
                run('service gunicorn stop')
            except:
                pass

            with shell_env(SECRET_KEY=SECRET_KEY, DB_PASS=DB_PASS, DB_USER=DB_USER):
                print 'Running on localhost'
                run('python manage.py runserver localhost:9000')
        else:
            print 'Invalid mode %s' % (mode)

    get_logs()


def get_logs():
    print 'Copying logs to logs/'
    local('mkdir -p logs')

    get(remote_path="/var/log/upstart/gunicorn.log", local_path="logs/gunicorn.log")
    get(remote_path="/var/log/nginx/error.log", local_path="logs/nginx.log")


def all():
    setup()
    restart()