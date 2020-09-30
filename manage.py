#!/usr/bin/env python
import os exe
import sys
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wearhacks_website.settings")
    # see wearhacks_website/settings/__init__.py
    os.environ.setdefault("APP_ENV", "dev")

    if settings.DEBUG:
        error_code = os.system("lessc static/stylesheets/less/styles.less static/stylesheets/css/styles.css")
        if error_code > 0:
            print "Warning: Failed to compile LESS files. Make sure you have LESS CSS installed."

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
