"""
Script to perform common operations on remote server from local machine.

Prerequisites:
    pip install fabric
    Create DigitalOcean droplet with Django installation
    Copy server_files/fab_config_example.py to server_files/fab_config.py and edit in your settings

If you're starting fresh, use command: fab all. 

For detailed information on a specific command, use: fab -d <command>
"""

import fabtools
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.context_managers import shell_env
import tempfile, os, sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCAL_DJANGO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not os.path.exists('fab_config.py'):
    print 'Please create a fab_config.py file, see fab_config_example.py'
    sys.exit()

try:
    from fab_config import (
        DEFAULT_MODE, 
        DEFAULT_DEPLOY_TO,
        DEPLOYMENT_MODES,
        DEPLOYMENT_PRIVATE_FILES,
        DEPLOYMENT_HOSTS,
        DEFAULT_BRANCH,
        DJANGO_PASS)
except ImportError, e:
    print e
    print 'Please update fab_config.py, see fab_config_example.py'
    sys.exit()

print """
Default settings: 
   - Deploying to %s host %s with mode %s. 
   - Using private file %s.
   - Using branch %s
   - Django pass %s

For a list of commands use: fab -l
""" % (
    DEFAULT_DEPLOY_TO, 
    DEPLOYMENT_HOSTS[DEFAULT_DEPLOY_TO],
    DEFAULT_MODE,
    os.path.join(LOCAL_DJANGO_PATH, 'wearhacks_website',
            'settings', DEPLOYMENT_PRIVATE_FILES[DEFAULT_DEPLOY_TO] + '.py'),
    DEFAULT_BRANCH,
    DJANGO_PASS)

########### DJANGO SETTINGS
DJANGO_SETTINGS_MODULE = 'wearhacks_website.settings'
########### END DJANGO SETTINGS

########### PROMPT SETTINGS
AUTO_ANSWER_PROMPTS = True  
if AUTO_ANSWER_PROMPTS:
    prompts = {
        'Do you want to continue [Y/n]? ': 'Y',
        '? May bower anonymously report usage statistics to improve the tool over time? (Y/n)': 'Y',
        "Type 'yes' to continue, or 'no' to cancel: ": 'yes',
        'Would you like to create one now? (yes/no): ': 'no'
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

########### ENV VARIABLES ON REMOTE
env.hosts = DEPLOYMENT_HOSTS[DEFAULT_DEPLOY_TO]
ENV_VARIABLES = {
    'DJANGO_SETTINGS_MODULE': 'wearhacks_website.settings',
    'PYTHONPATH': DJANGO_PROJECT_PATH
}
########### END ENV VARIABLES

########### FAB ENV
env.user = 'root'
env.project_root = DJANGO_PROJECT_PATH
env.colorize_errors = True
########### END FAB ENV

def _write_file(local_path, remote_path, options):
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

def setup(mode=DEFAULT_MODE, deploy_to=DEFAULT_DEPLOY_TO, branch=DEFAULT_BRANCH):
    """
    Sets up a DigitalOcean server 'droplet' using a Django One-Click Install Image.

    Prerequisites
    --------
    Create DigitalOcean droplet with Django installation

    Overview
    --------
    Installs git and package managers (npm, bower)
    Add correct permission to static folder
    Clones github directory and installs python + bower requirements
    Updates configuration files (see update_conf_files)

    Options
    -------
        mode
            default: DEFAULT_MODE
        deploy_to
            default: DEFAULT_DEPLOY_TO
        branch [DEFAULT_BRANCH]
            git branch to pull from

    fab reboot
    =========
        (Setup step assumed to be completed.)
        Pull changes from master repo
        Migrate database
        Restart nginx and gunicorn
        Run project using production settings (see wearhacks_website/settings/prod.py)

        
    """
    env.hosts = DEPLOYMENT_HOSTS[deploy_to]

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
                'node-less',
                'gettext'
            ])

        try:
            run('ln -s /usr/bin/nodejs /usr/bin/node')
        except:
            pass

        NPM_PACKAGES = (
            'bower', 
            )
        with settings(prompts=prompts, warn_only=True):
            for package in NPM_PACKAGES:
                print 'Installing %s as root...' % (package)
                sudo('npm install -g %s' % (package))


        print 'Making django project directory at %s...' % (DJANGO_PROJECT_DIR)
        run('mkdir -p %s' % (DJANGO_PROJECT_DIR))

        if not os.path.exists(DJANGO_PROJECT_PATH):
            with cd(DJANGO_PROJECT_DIR):
                print 'Cloning Github Project into %s...' % (DJANGO_PROJECT_NAME)
                run('git clone %s %s' % (GITHUB_PROJECT, DJANGO_PROJECT_NAME)) 

        with cd(DJANGO_PROJECT_PATH):
            pull_changes(mode=mode, deploy_to=deploy_to, branch=branch)

        run("git config --global core.filemode false")
        update_conf_files(deploy_to=deploy_to)
        update_permissions(setup=True)

def compile_messages(mode=DEFAULT_MODE):
    env_variables = _get_env_variables(mode=mode) 
    with shell_env(**env_variables):
        # with cd(DJANGO_PROJECT_PATH):
        #     run('django-admin makemessages -x js -l fr')
        # with cd(os.path.join(DJANGO_PROJECT_PATH, 'static', 'javascripts')):
        #     run('django-admin makemessages -d djangojs -l fr')
        with cd(DJANGO_PROJECT_PATH):
            run('django-admin compilemessages')

def _update_permissions(debug=False, setup=False, only_static=False):
    """
    An exhaustive fail-proof permission setup. I tried to give the least possible 
    permissions.
    """
    print 'Updating permissions'
    with settings():

        with cd('/home'):
            sudo("find -type d -exec chmod a+x {} \;"); # makre sure all directories are executable

        if setup and not only_static:
            with settings(warn_only=True):
                sudo('groupadd staticusers')
                sudo('adduser www-data staticusers')
                sudo('adduser django staticusers')

        if setup:
            with cd(DJANGO_PROJECT_PATH):
                run('mkdir -p media')
                run('mkdir -p assets')
                run('mkdir -p registration/migrations')

        # change permissions to static files
        sudo('chown -R django %s' % (DJANGO_PROJECT_PATH))
        sudo('chgrp -R staticusers %s' % (os.path.join(DJANGO_PROJECT_PATH, 'assets')))
        sudo('chgrp -R staticusers %s' % (os.path.join(DJANGO_PROJECT_PATH, 'media')))

        with cd(DJANGO_PROJECT_PATH):    
            # all files under the project dir are owned by django (gunicorn's uid) is the owner
            if not only_static:
                sudo("chmod -R 500 .") # r-x --- --- : django can only read and execute files by default
                with settings(warn_only=True):
                    sudo("chmod -R 700 registration/migrations") # rwx --- --- : django can write new migrations
            
            sudo("chmod -R 644 assets") # rw- r-- r-- : assets can be read by nginx (var-www) as well as everyone else
            sudo("chmod -R 644 media") # rw- r-- r--

            if not only_static:
                sudo("chmod -R 200 server_files/logs") # -w- r-- r--
                blacklist = (
                    'scripts',
                    # 'wearhacks_website/settings/*_private.py',
                )

                for f in blacklist:
                    sudo("chmod -R 000 %s" % (f))

            sudo("find -type d -exec chmod a+x {} \;") # set all directories to executable            
            run("ls -la")

            if debug:
                with settings(warn_only=True):
                    env.user = 'django'
                    run('python manage.py runserver')
        

def update_permissions(deploy_to=DEFAULT_DEPLOY_TO, mode=DEFAULT_MODE, setup=False):
    _update_permissions(setup=setup)
    restart_nginx()
    restart_gunicorn()

def update_conf_files(deploy_to=DEFAULT_DEPLOY_TO, restart=True):
    """
    Updates private django settings file as well as .profile, nginx and gunicorn configs
    
    Options
    -------
        deploy_to [DEFAULT_DEPLOY_TO]
        restart [True]
            Whether or not to restart nginx and gunicorn
    """
    env.hosts = DEPLOYMENT_HOSTS[deploy_to]
    _update_private_settings_file(deploy_to=deploy_to)

    print 'Modifying ~/.profile'
    _write_file('.profile', '.profile',
        {
            'DJANGO_PROJECT_PATH': DJANGO_PROJECT_PATH
        })

    print 'Modifying nginx config'
    _write_file('nginx.sh', '/etc/nginx/sites-enabled/django',
        {
            'DJANGO_PROJECT_PATH': DJANGO_PROJECT_PATH
        })

    print 'Modifying gunicorn config'
    _write_file('gunicorn.sh', '/etc/init/gunicorn.conf',
        {
            'DJANGO_PROJECT_DIR': DJANGO_PROJECT_DIR,
            'DJANGO_PROJECT_NAME': DJANGO_PROJECT_NAME,
            'DJANGO_APP_NAME': DJANGO_APP_NAME
        })
    if restart:
        print 'Restarting nginx'
        sudo('nginx -t')
        sudo('service nginx reload')

        print 'Restarting gunicorn'
        run('service gunicorn restart')

def test_models(mode=DEFAULT_MODE, deploy_to=DEFAULT_DEPLOY_TO):
    """
    Generate random data using registration/management/comands/generate_registrations.py.
    """
    print '\nTesting models'
    env_variables = _get_env_variables(mode=mode) 
    with cd(DJANGO_PROJECT_PATH):
        with shell_env(**env_variables):
            print '> Check database backend'
            run('echo "from django.db import connection;connection.vendor" | python manage.py shell ')

            print '> Generate random registrations'
            run('python manage.py generate_registrations 10 --reset')

def _get_private_settings(deploy_to=DEFAULT_DEPLOY_TO):
    private_file = _get_private_settings_file(deploy_to=DEFAULT_DEPLOY_TO, local=True)
    import imp
    private = imp.load_source('', private_file)
    return private

def reset_db(mode=DEFAULT_MODE, deploy_to=DEFAULT_DEPLOY_TO):
    """
    Delete database and perform migrations (see migrate).

    Options
    -------
        mode [DEFAULT_MODE]
        deploy_to [DEFAULT_DEPLOY_TO]
    """
    with (hide('stdout')):
        pull_changes(mode=mode, deploy_to=deploy_to)
    migrate(mode=mode, deploy_to=deploy_to, reset_db=True)

def migrate(mode=DEFAULT_MODE, deploy_to=DEFAULT_DEPLOY_TO, env_variables=None,
    setup=False, reset_db=False, generate_dummy_data=True, create_super_user=True):
    """
    Perform migrations.

    Options
    -------
        mode [DEFAULT_MODE]
        deploy_to [DEFAULT_DEPLOY_TO]
        reset_db [False]
            If True, delete the database.
        generate_dummy_data [True]
            Generate dummy data (see registration/management/)
        createsuperuser [True]
            If True and reset_db is True, create admin super user.
    """
    if not env_variables:
        env_variables = _get_env_variables(mode=mode)

    print '\nMigrating database as user django'

    with shell_env(**env_variables):
        with cd(DJANGO_PROJECT_PATH):
            if reset_db:
                with settings(warn_only=True):
                    run('rm -rf registration/migrations')
                with settings(warn_only=True):
                    sudo("chmod -R 700 registration") # rwx --- --- : django can write new migrations

            env.user = 'django'
            env.password = DJANGO_PASS

            print '> Checking database backend'
            run('echo "from django.db import connection; connection.vendor" | python manage.py shell')

            # get django database pass, this is kind of hacky but wtv
            private_settings = _get_private_settings(deploy_to=deploy_to)
            django_db_pass = private_settings.DB_PASS
            with settings(prompts={
                "Password for user django: ": django_db_pass}):
                if reset_db:
                    print '> Deleting database'
                    if mode == 'dev':
                        run('rm -rf wearhacks_website/db.sqlite3')
                    else:
                        with settings(warn_only=True):
                            run('rm -rf registration/migrations')
                        run('python manage.py sqlclear registration | python manage.py dbshell ')

                run('python manage.py makemigrations')
                if setup:
                    run('python manage.py migrate --fake-initial') 
                    run('python manage.py makemigrations registration')
                    run('python manage.py migrate registration') 
                elif reset_db:
                    run('python manage.py migrate --fake')     
                    run('python manage.py makemigrations registration')
                    run('python manage.py migrate --fake-initial')
                    run('python manage.py migrate')
                else:
                    run('python manage.py migrate')
            if mode == 'dev' or reset_db:
                if generate_dummy_data or reset_db:
                    run('python manage.py generate_registrations 3 --reset')
            env.user = 'root'
            
            if mode == 'prod':
                print '> Checking postgresql status'
                run('service postgresql status')
                run('sudo netstat -nl | grep postgres')
            
            print '> Creating super user with login admin/pass'
            with settings(warn_only=True):
                with hide('stderr', 'stdout', 'warnings'):
                    sudo('chmod u+x scripts/createsuperuser.sh')
                    run('./scripts/createsuperuser.sh')

def update_requirements(branch=DEFAULT_BRANCH):
    """
    Update pip and bower requirements
    """
    print '\nUpdate pip and bower requirements'
    with cd(DJANGO_PROJECT_PATH):
        print 'Installing python requirements..'
        run('pip install -r requirements.txt')
        
        print 'Installing bower requirements..'
        run('bower install --allow-root')

def pull_changes(mode=DEFAULT_MODE, deploy_to=DEFAULT_DEPLOY_TO, branch=DEFAULT_BRANCH,
    collectstatic=False):
    """
    Update conf files, pull changes from repo and update requirements.

    Options
    -------
        mode [DEFAULT_MODE]
        deploy_to [DEFAULT_DEPLOY_TO]
        branch [DEFAULT_BRANCH]
            git branch to pull from

    See
    -------
        update_requirements
    """
    _update_private_settings_file(deploy_to=deploy_to)
    with cd(DJANGO_PROJECT_PATH):
        print '\nPulling changes from %s repo' % (branch)
        run('git config --global core.filemode false')
        if False: #branch == 'stable':
            run('git fetch --all')
            run('git reset --hard origin/%s' % (branch))
        else:
            run('git checkout .') # discard changes in working directory
            run('git pull origin %s' % (branch))
            run('git checkout %s' % (branch))
        update_requirements()

    if collectstatic:
        compile_messages(mode=mode)
        collect_staticfiles(mode=mode, deploy_to=deploy_to)
        restart_gunicorn()

def _update_private_settings_file(deploy_to=DEFAULT_DEPLOY_TO):
    print '\nUpdating private settings'
    local_private_file = _get_private_settings_file(local=True, deploy_to=deploy_to)
    remote_private_file = _get_private_settings_file(local=False, deploy_to=deploy_to)
    put(local_path=local_private_file,remote_path=remote_private_file)

def _get_private_settings_file(deploy_to=DEFAULT_DEPLOY_TO, local=True):
    if deploy_to not in DEPLOYMENT_PRIVATE_FILES.keys():
        print 'Unknown deployment option %s' % (deploy_to)
        print 'Possible options:', DEPLOYMENT_PRIVATE_FILES.keys()
        sys.exit()

    basename = DEPLOYMENT_PRIVATE_FILES[deploy_to]

    if local:
        django_path = LOCAL_DJANGO_PATH
        private_file = os.path.join(django_path, 'wearhacks_website',
            'settings', basename + '.py')
    else:
        django_path = DJANGO_PROJECT_PATH
        private_file = os.path.join(django_path, 'wearhacks_website',
            'settings', 'private.py')
    return private_file

def _get_env_variables(mode=DEFAULT_MODE, deploy_to=DEFAULT_DEPLOY_TO):
    ev = dict(ENV_VARIABLES)
    if mode not in DEPLOYMENT_MODES:
        print 'Invalid mode option %s' % (mode)
        print 'Possible options:', DEPLOYMENT_MODES
        sys.exit()
    ev['APP_ENV'] = mode
    env.hosts = DEPLOYMENT_HOSTS[deploy_to]
    return ev

def hard_reboot(**kwargs):
    """
    Reboot server and reset database (see reboot)
    """
    kwargs["reset_db"] = True
    reboot(**kwargs)

def restart_gunicorn():
    print 'Restarting gunicorn'
    run('service gunicorn restart')

def restart_nginx():
    print 'Restarting nginx'
    sudo('nginx -t')
    sudo('service nginx restart')

def collect_staticfiles(mode=DEFAULT_MODE, deploy_to=DEFAULT_DEPLOY_TO,
        env_variables=None):
    if not env_variables:
        env_variables = _get_env_variables(mode=mode, deploy_to=deploy_to)

    with cd(DJANGO_PROJECT_PATH):
        with shell_env(**env_variables):
            with settings(prompts=prompts):
                compile_messages(mode=mode)
                run('python manage.py collectstatic')
        _update_permissions(only_static=True, setup=setup)
        restart_nginx()

def reboot(mode=DEFAULT_MODE, deploy_to=DEFAULT_DEPLOY_TO, env_variables=None, 
    setup=False, reset_db=False, branch=DEFAULT_BRANCH):
    """
    Reboot server.

    Prerequisites
    -------------
        fab setup
    
    Overview
    -------------
        Update conf files (see update_conf_files)
        Pull changes from repo (see pull_chages)
        Migrate database (see migrate)
        Collects static files
        Restart nginx
        If mode is dev, stop gunicorn and run localhost
        If mode is prod, restart gunicorn
        Updates logs (see get_logs)

    Options
    -------------
        mode [DEFAULT_MODE]
        deploy_to [DEFAULT_DEPLOY_TO]
        env_variables [None]
            dictionary of env variables to pass to remote shell env
            see: _get_env_variables
        reset_db [False]
            whether or not to delete database
        branch [DEFAULT_BRANCH]
            git branch to pull from
    """
    if not env_variables:
        env_variables = _get_env_variables(mode=mode, deploy_to=deploy_to)
    
    with cd(DJANGO_PROJECT_PATH):
        print 'Stopping gunicorn' 
        with settings(warn_only=True):
            run('service gunicorn stop')

        pull_changes(mode=mode, deploy_to=deploy_to)
        with shell_env(**env_variables):
            with settings(prompts=prompts):
                compile_messages(mode=mode)
                run('python manage.py collectstatic')
        _update_permissions(only_static=True, setup=setup)
        
        restart_nginx()

        migrate(mode=mode, deploy_to=deploy_to, env_variables=env_variables, 
            setup=setup, reset_db=reset_db)

        if mode == 'prod':

            if deploy_to == 'alpha':
                with shell_env(**env_variables):
                    print 'Generating 3 random registration...'
                    run('python manage.py generate_registrations 3')

            print 'Restarting gunicorn'
            run('service gunicorn restart')
            get_logs(deploy_to=deploy_to)

        elif mode == 'dev':
            get_logs(deploy_to=deploy_to)
            with shell_env(**env_variables):
                print 'Running on localhost'
                run('python manage.py runserver localhost:9000')
        else:
            print 'Invalid mode %s' % (mode)

def get_media(deploy_to=DEFAULT_DEPLOY_TO):
    """
    Copy server's media folder
    """
    print '\nCopying media to server_files/media/'
    log_dir = os.path.join(LOCAL_DJANGO_PATH, 'server_files', 'media', deploy_to)
    if not os.path.exists(log_dir):
        local('mkdir -p %s' % (log_dir))
    with settings(hide('warnings')): 
        get(remote_path="%s/media" % (DJANGO_PROJECT_PATH), local_path="%s" % (log_dir))

def generate_registrations(n=3, mode=DEFAULT_MODE):
    env_variables = _get_env_variables(mode=mode) 
    with shell_env(**env_variables):
        with cd(DJANGO_PROJECT_PATH):
            print 'Generating %i random registration...' % (n)
            run('python manage.py generate_registrations %i' % (n))

def update_challenge_questions(deploy_to=DEFAULT_DEPLOY_TO, reset=False, mode=DEFAULT_MODE):
    # update csv in tmp
    print os.path.join(LOCAL_DJANGO_PATH, 'tmp/crypto_texts.csv')
    with cd(DJANGO_PROJECT_PATH):
        run('mkdir -p tmp')
    _write_file(
        os.path.join(LOCAL_DJANGO_PATH, 'tmp/crypto_texts.csv'), 
        os.path.join(DJANGO_PROJECT_PATH, 'tmp/crypto_texts.csv'), {})
    _write_file(
        os.path.join(LOCAL_DJANGO_PATH, 'registration/management/commands/encrypter.py'), 
        os.path.join(DJANGO_PROJECT_PATH, 'registration/management/commands/encrypter.py'), {})
    env_variables = _get_env_variables(mode=mode) 
    with cd(DJANGO_PROJECT_PATH):
        with shell_env(**env_variables):
            if reset:
                run('python manage.py generate_challenges tmp/crypto_texts.csv --reset')
            else:
                run('python manage.py generate_challenges tmp/crypto_texts.csv')                

def get_fixtures(deploy_to=DEFAULT_DEPLOY_TO, mode=DEFAULT_MODE):
    from datetime import datetime
    env_variables = _get_env_variables(mode=mode) 
    apps = ('registration', 'event')
    for app in apps:
        fixture_path = '%s/fixtures/%s-data-%s.json' % (
            app, app, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        with shell_env(**env_variables):
            with cd(DJANGO_PROJECT_PATH):
                run('mkdir -p %s/fixtures' % (app))
                run('python manage.py dumpdata --format=json --indent=2 %s > %s' % (app, fixture_path))
        log_dir = os.path.join(LOCAL_DJANGO_PATH, 'server_files', 'fixtures', deploy_to)
        if not os.path.exists(log_dir):
            local('mkdir -p %s' % (log_dir))
        with settings(hide('warnings')): 
            get(remote_path="%s/%s" % (DJANGO_PROJECT_PATH, fixture_path), local_path="%s" % (log_dir))

def get_logs(deploy_to=DEFAULT_DEPLOY_TO):
    """
    Copy django, nginx and gunicorn log files from remote to server_files/logs
    """
    print '\nCopying logs to server_files/logs/'
    log_dir = os.path.join(LOCAL_DJANGO_PATH, 'server_files', 'logs', deploy_to)
    if not os.path.exists(log_dir):
        local('mkdir -p %s' % (log_dir))
    with settings(hide('warnings')): 
        get(remote_path="/var/log/nginx/error.log", local_path="%s/nginx.error.log" % (log_dir))
        get(remote_path="/var/log/nginx/access.log", local_path="%s/nginx.access.log" % (log_dir))

        get(remote_path="%s/server_files/logs/local/django.debug.log" % (DJANGO_PROJECT_PATH), local_path="%s/django.debug.log" % (log_dir))
        get(remote_path="%s/server_files/logs/local/django.request.debug.log" % (DJANGO_PROJECT_PATH), local_path="%s/django.request.debug.log" % (log_dir))

        get(remote_path="/var/log/upstart/gunicorn.log", local_path="%s/gunicorn.log" % (log_dir))
        get(remote_path="/var/log/postgresql/postgresql-9.3-main.log", local_path="%s/psql.main.log" % (log_dir))

def all(deploy_to=DEFAULT_DEPLOY_TO, mode=DEFAULT_MODE):
    """Setup and reboot."""
    setup(deploy_to=deploy_to, mode=mode)
    reboot(deploy_to=deploy_to, mode=mode, setup=True)