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

import fabtools
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.context_managers import shell_env
import tempfile, os, sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from wearhacks_website.settings.private import *
except ImportError:
    print 'ERROR: You must make a private.py file (see wearhacks_website/settings/private_example.py)'
    from wearhacks_website.settings.private_example import *
    sys.exit() # comment out this line if you want to use the example private settings

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
        '? May bower anonymously report usage statistics to improve the tool over time? (Y/n)': 'Y',
        "Type 'yes' to continue, or 'no' to cancel: ": 'yes'
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
ENV_VARIABLES = {
    'DB_NAME': DB_NAME,
    'DB_USER': DB_USER,
    'DB_PASS': DB_PASS,
    'DB_HOST': 'localhost', #HOSTS[0], #'localhost' #HOSTS[0]
    'DB_PORT': str(DB_PORT)
}
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
            # Require some Debian/Ubuntu packages
            fabtools.require.deb.packages([
                'git',
                'npm',
                'libpq-dev',
                'python-dev',
                'postgresql',
                'postgresql-contrib',
                'nginx',
                'gunicorn',
                'sqlite3',
                'node-less'
            ])

        if not os.path.isfile('/usr/bin/node'):
            run('ln -s /usr/bin/nodejs /usr/bin/node')

        NPM_PACKAGES = (
            'bower', 
            )
        with settings(prompts=prompts):
            for package in NPM_PACKAGES:
                print 'Installing %s as root...' % (package)
                sudo('npm install -g %s' % (package))

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

            reset_postgres_db()

def reset_postgres_db():
    # Require a PostgreSQL server
    # fabtools.require.postgres.server()
    if  fabtools.postgres.user_exists(DB_USER):
        print 'Deleting superuser %s' % (DB_USER)
        fabtools.postgres.drop_user(DB_USER)

    print 'Creating new superuser %s' % (DB_USER)
    try:
        fabtools.postgres.create_user(DB_USER, DB_PASS, 
            superuser=True, createrole=True)
    except:
        fabtools.postgres.create_user(DB_USER, DB_PASS, 
            superuser=True, createrole=False)

    # Remove DB if it exists
    if fabtools.postgres.database_exists(DB_NAME):
        print 'Dropping database %s ' % (DB_NAME)
        fabtools.postgres.drop_database(DB_NAME)

    print 'Creating new database %s' % (DB_NAME)
    fabtools.postgres.create_database(DB_NAME, owner=DB_USER)
    test_models()

def update_conf_files():
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
    print 'Restarting nginx'
    sudo('nginx -t')
    sudo('service nginx reload')

    print 'Restarting gunicorn'
    run('service gunicorn restart')

def test_models(mode='prod'):
    env_variables = get_env_variables(mode=mode) 
    with cd(DJANGO_PROJECT_PATH):
        with shell_env(**env_variables):
            print 'Check database backend'
            run('echo "from django.db import connection;connection.vendor" | python manage.py shell ')
            print 'In case you forgot the password, here it is %s' % (env_variables['DB_PASS'])
            run('python manage.py sqlclear registration | python manage.py dbshell ')

            pull_changes()
            migrate(mode=mode)
            run('python manage.py generate_registrations 10 --reset')

def migrate(mode='prod', env_variables=None):
    if not env_variables:
        env_variables = get_env_variables(mode=mode)

    print 'Migrating database'
    
    with shell_env(**env_variables):

        with cd(DJANGO_PROJECT_PATH):
            # run('echo "from django.db import connection; connection.vendor" | python manage.py shell')
            if mode == 'dev':
                run('python manage.py sqlclear registration | python manage.py dbshell ')
            else:
                run('service postgresql status')
                run('sudo netstat -nl | grep postgres')

            run('python manage.py makemigrations')
            run('python manage.py migrate')
            run('python manage.py syncdb')

            # create superuser
            try:
                with hide('stderr', 'stdout'):
                    sudo('chmod u+x scripts/createsuperuser.sh')
                    run('./scripts/createsuperuser.sh')
            except:
                pass

def update_requirements():
    with cd(DJANGO_PROJECT_PATH):
        run('git pull origin master')
        print 'Installing python requirements..'
        run('pip install -r requirements.txt')
        
        print 'Installing bower requirements..'
        run('bower install --allow-root')

        # setup proper permissions
        sudo('chown -R django:django %s' % (os.path.join(DJANGO_PROJECT_PATH, 'static')))


def pull_changes():
    print 'Updating private.py'
    put(local_path="../wearhacks_website/settings/private.py",
        remote_path=os.path.join(DJANGO_PROJECT_PATH, 
            "wearhacks_website/settings/private.py")
        )
    
    with cd(DJANGO_PROJECT_PATH):
        print 'Pulling changes from master repo'
        run('git pull origin master')
        run('pip install -r requirements.txt')

def get_env_variables(mode='prod'):
    ev = dict(ENV_VARIABLES)
    if mode == 'dev':
        ev["DJANGO_SETTINGS_MODULE"] = DEV_DJANGO_SETTINGS_MODULE
        ev["SECRET_KEY"] = TEST_SECRET_KEY
    elif mode == 'prod':
        ev["DJANGO_SETTINGS_MODULE"] = PROD_DJANGO_SETTINGS_MODULE
        ev["SECRET_KEY"] = PROD_SECRET_KEY
    else:
        print 'Invalid mode %s' % (mode)
    return ev

def reboot(mode='prod', env_variables=None):
    if not env_variables:
        env_variables = get_env_variables(mode=mode)

    with cd(DJANGO_PROJECT_PATH):
        pull_changes()
        migrate(mode=mode, env_variables=env_variables)

        if mode == 'prod':
            print 'Restarting nginx'
            sudo('nginx -t')
            sudo('service nginx reload')

            print 'Restarting gunicorn'
            run('service gunicorn restart')
            with shell_env(**env_variables):
                with settings(prompts=prompts):
                    run('python manage.py collectstatic')

            with shell_env(**env_variables):
                print 'Generating 1 random registration...'
                run('python manage.py generate_registrations 1')

        elif mode == 'dev':
            print 'Restarting nginx'
            sudo('nginx -t')
            sudo('service nginx reload')

            print 'Stopping gunicorn' 
            try:
                run('service gunicorn stop')
            except:
                pass

            with shell_env(**env_variables):
                print 'Running on localhost'
                run('python manage.py generate_registrations 10 --reset')
                run('python manage.py runserver localhost:9000')
        else:
            print 'Invalid mode %s' % (mode)
    
    sudo('chown -R django:django %s' % (os.path.join(DJANGO_PROJECT_PATH, 'static')))
    get_logs()


def get_logs():
    print 'Copying logs to logs/'
    local('mkdir -p logs')

    get(remote_path="/var/log/upstart/gunicorn.log", local_path="logs/gunicorn.log")
    get(remote_path="/var/log/nginx/error.log", local_path="logs/nginx.log")
    get(remote_path="tail /var/log/postgresql/postgresql-9.3-main.log", local_path="logs/postgresql.log")


def all():
    setup()
    reboot(mode='prod')