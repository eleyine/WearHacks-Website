from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as __

import re
from django.core.validators import RegexValidator
from event.helpers import get_profile_pic_filename

class Person(models.Model):
    PERSON_CATEGORIES = (
        ('O', _('Other')),
        ('J', _('Judge')),
        ('M', _('Mentor')),
    )

    alpha = RegexValidator(regex=re.compile(r'^[\w\s]*$', flags=re.UNICODE), message=_('Only letters are allowed.'))
    numeric = RegexValidator(regex=re.compile(r'^[\d]*$', flags=re.UNICODE), message=_('Only numbers are allowed.'))

    category = models.CharField(max_length=20, 
        choices=PERSON_CATEGORIES, 
        default=PERSON_CATEGORIES[0][0],
        )

    first_name = models.CharField(max_length=30, validators=[alpha])
    last_name = models.CharField(max_length=30, validators=[alpha])

    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        # Translators: Gender information
        ('N', _('Other / I prefer not to disclose')),
    )
    gender = models.CharField(max_length=20, 
        choices=GENDER_CHOICES, 
        # default=GENDER_CHOICES[0][0],
        verbose_name=_('gender')
        )

    profile_pic = models.ImageField(blank=True, 
        upload_to=get_profile_pic_filename,
        help_text="Please make sure it's a square picture.")

    telephone = models.CharField(max_length=10, blank=True, validators=[numeric])

    company = models.CharField(max_length=100, blank=True)
    company_link = models.URLField(max_length=100, blank=True)

    rank = models.IntegerField(
        default=999, 
        help_text=_('For internal use. '
            'Determines the order in which this person appears on the website.')
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    role = models.CharField(max_length=100, 
        help_text="Appears under the person's name", blank=True)
    biography = models.TextField(blank=True)

    # social icons
    email = models.EmailField(blank=True)
    website = models.URLField(max_length=100, blank=True)
    twitter = models.URLField(max_length=100, blank=True)
    facebook = models.URLField(max_length=100, blank=True)
    github = models.URLField(max_length=100, blank=True)
    linkedin = models.URLField(max_length=100, blank=True)

    def full_name(self):
        return '%s %s' % (self.first_name.encode('utf-8'), 
            self.last_name.encode('utf-8'))
    full_name.admin_order_field = 'last_name'

    def has_twitter(self):
        return bool(self.twitter)

    def has_linkedin(self):
        return bool(self.linkedin)

    def has_website(self):
        return bool(self.website)

    def has_email(self):
        return bool(self.email)

    def has_facebook(self):
        return bool(self.facebook)

    def has_github(self):
        return bool(self.github)

    def has_telephone(self):
        return bool(self.telephone)

    class Meta:
        ordering = ('-updated_at', 'category', 'last_name', 'rank',)

