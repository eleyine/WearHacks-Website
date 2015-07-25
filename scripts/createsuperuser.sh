#!/bin/bash

# LOL DON'T DO THIS IN PRODUCTION
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@wearhacks.com', 'pass')" | python manage.py shell