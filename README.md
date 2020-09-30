# Wearhacks Montreal 2015 Website Source

## Branches

* `master`: most up-to-date branch with open registration. Up on <http://wearhacks.eleyine.com>
* `stable`: deployed branch with registration closed. Live on <http://montreal.wearhacks.com>

# Installation

## Requirements

* `pip` - instructions [here](https://pip.pypa.io/en/latest/installing.html)
* `virtualenvwrapper` - instructions [here](https://virtualenvwrapper.readthedocs.org/en/latest/install.html)
* `npm` - instructions [here](https://docs.npmjs.com/getting-started/installing-node)

## Quick setup

```bash
$ git clone git@github.com:eleyine/WearHacks-Website.git
$ cd WearHacks-Website
$ chmod u+x setup.sh
# The next two steps are optional but strongly recommended
$ mkvirtualenv wearhacks-website
$ workon wearhacks-website
(wearhacks-website) $ ./setup.sh
```

**Note**: `setup.sh` will copy `example_private_settings.py` to `private.py`. If you are on your local machine in dev mode, there's no need to edit it. However, if you'd like to deploy, *please update `wearhacks_website/settings/private.py` with your sensitive and deployment-specific settings*.

**Manual install: what's in `setup.sh`?**

If you don't want to use `setup.sh`

```bash
$ mkvirtualenv wearhacks-website
$ workon wearhacks-website
(wearhacks-website) $ pip install -r requirements.txt
(wearhacks-website) $ bower install
(wearhacks-website) $ cp wearhacks_website/settings/example_private_settings.py wearhacks_website/settings/private.py
(wearhacks-website) $ python manage.py makemigrations
(wearhacks-website) $ python manage.py migrate
(wearhacks-website) $ python manage.py generate_registrations 3
(wearhacks-website) $ python manage.py runserver
```

Now, open <http://127.0.0.1:8000/>.

## Usage

* To run on [localhost](http://127.0.0.1:8000/):

    ```bash
    $ workon wearhacks-website
    (wearhacks-website) $ python manage.py runserver
    ```

* By default, you will use the Django settings defined in `wearhacks_settings/settings/dev.py`. 
* To use production settings defined in `wearhacks_settings/settings/prod.py`:

    ```bash
    (wearhacks-website) $ export APP_ENV=prod
    (wearhacks-website) $ python manage.py runserver
    ```

* You can edit `wearhacks_settings/settings/private.py` to enter sensitive and user-specific settings. All settings in `private.py` will override those defined in `dev.py` and `prod.py`. See `wearhacks_website/settings/__init__.py` for more information.

## Stripe settings

The registration app handles payment via [Stripe](https://stripe.com). To test this feature, edit in your Stripe API keys in your private settings files (`wearhacks_website/*private.py`).

## Deployment on Digital Ocean

I wrote a `fabric` script to automate installation on Digital Ocean droplets using the one-step Django installation. If you are deploying elsewhere, you can have an idea of the steps to take by inspecting `server_files/fabfile.py`. 

Here are the setup instructions if you choose to do it with Digital Ocean. 

* Create a Digital Ocean droplet with a Django installation image
* Ssh into your droplet to obtain the postgresql database password. It will be displayed in the welcome message. 
* Copy `wearhacks_website/settings/private.py` to `wearhacks_website/settings/server_private.py` and uncomment the postgresql settings. Edit in your postgresql password from the step above.

* Make sure you have fabric installed locally. If you run `setup.sh`, you already have it.
* In `wearhacks_website/server_files/`, copy `fab_config_example.py` and rename it to `fab_config.py`. Edit in in your deployment host address.
* Then in `server_files`, run `fab all`
* If you'd like a list of fab commands, run `fab -l`
