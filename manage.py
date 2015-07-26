#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wearhacks_website.settings.local")

    # Normally you should not import ANYTHING from Django directly
    # into your settings, but ImproperlyConfigured is an exception.
    from django.core.exceptions import ImproperlyConfigured

    try: 
        os.environ['SECRET_KEY']
    except KeyError:
        error_msg = ("Set the SECRET_KEY env variable. Use:\n"
            "\texport SECRET_KEY=<YOUR_SECRET_KEY>")
        raise ImproperlyConfigured(error_msg)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
