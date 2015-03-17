# Pyladies Django Workshop Boilerplate

## Requirements

* `git` - instructions [here](http://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* `pip` - instructions [here](https://pip.pypa.io/en/latest/installing.html)
* `virtualenvwrapper` - instructions [here](https://virtualenvwrapper.readthedocs.org/en/latest/install.html)
* `npm` (node package manager) - instructions [here](https://docs.npmjs.com/getting-started/installing-node)

## Installation

1. If you have a github account, fork this repository using:
```bash
$ git clone git@github.com:<your username>/pyladies-django-workshop.git
$ git reset --hard boilerplate
```

1. (bis) If you don't have a github account:
```bash
$ git clone git@github.com:eleyine/pyladies-django-workshop.git
$ git reset --hard boilerplate
```

2. Set up vitualenv:

```bash
$ mkvirtualenv pyladies-django
$ workon pyladies-django
$ cd pyladies-django-workshop
$ pip install -r requirements.txt
```

3. Install bower dependencies

```bash
$ npm install -g bower
# you might need to use $ sudo npm install -g bower
$ bower install
```

4. Migrate Django app models

```bash
$ python manage.py migrate
$ python manage.py runserver
```

5. Visit <http://localhost:8000/>, you should now see a blank page with a functional navbar and sidebar.

