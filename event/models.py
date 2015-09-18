from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as __

import re, datetime
from django.core.validators import RegexValidator
from event.helpers import get_profile_pic_filename, get_image_filename

class Workshop(models.Model):
    moderators = models.ManyToManyField('Person')

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    location = models.CharField(max_length=300, blank=True)
    time = models.DateTimeField()
    duration = models.IntegerField(default=60, 
        help_text='In minutes.')

    IMAGE_FOLDER = 'workshops'
    showcase_image = models.ImageField(
        upload_to=get_image_filename,
        help_text="Please make sure it's a transparent image (png).",
        blank=True)

    @property
    def all_moderators(self):
        return self.moderators.all()

    @property
    def human_readable_time_slot(self):
        start_time = self.time
        end_time = self.time + datetime.timedelta(0,self.duration*60)
        readable_time = '%s %s' % (
            datetime.datetime.strftime(start_time, '%A %I:%M%p - '),
            datetime.datetime.strftime(end_time, '%I:%M%p'),
        )
        return readable_time

    class Meta:
        ordering = ('time',)

    def __unicode__(self):
        return self.title

class Sponsor(models.Model):
    CATEGORIES = (
        ('ST', _('Local Standard')),
        ('PR', _('Local Premium')),
        ('GS', _('Global Standard')),
        ('GH', _('Global Premium')),
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=2, 
        choices=CATEGORIES, 
        default=CATEGORIES[0][0],
        )
    IMAGE_FOLDER = 'sponsors'
    image = models.ImageField(
        upload_to=get_image_filename,
        help_text="Please make sure it's a transparent image (png).")
    url = models.URLField(blank=True)

    def get_verbose_category(self):
        return dict(CATEGORIES)[self.category]

    def __unicode__(self):
        return self.name

class Person(models.Model):
    CATEGORIES = (
        ('O', _('Other')),
        ('J', _('Judge')),
        ('M', _('Mentor')),
    )

    alpha = RegexValidator(regex=re.compile(r'^[\w\s]*$', flags=re.UNICODE), message=_('Only letters are allowed.'))
    numeric = RegexValidator(regex=re.compile(r'^[\d]*$', flags=re.UNICODE), message=_('Only numbers are allowed.'))

    category = models.CharField(max_length=20, 
        choices=CATEGORIES, 
        default=CATEGORIES[0][0],
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

    def __unicode__(self):
        return self.full_name()

