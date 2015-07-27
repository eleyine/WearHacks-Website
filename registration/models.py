from django.db import models
import os, time, datetime

# Helpers
def get_resume_filename(instance, filename):
    return get_filename(instance, filename, directory='resumes')

def get_waiver_filename(instance, filename):
    return get_filename(instance, filename, directory='waivers')

def get_filename(instance, old_filename, directory=''):
    dirname = os.path.dirname(old_filename)
    # add time to differentiate between two registrees with the same first/last names
    suffix = datetime.datetime.now().strftime("__%m-%d_%H-%M")
    basename = '%s_%s_%s.pdf' % (instance.last_name, instance.first_name, suffix)
    filename = os.path.join(
        os.path.dirname(old_filename),
        directory,
        basename
        )
    return filename

class ChargeAttempt(models.Model):
    email = models.EmailField()
    charge_id = models.CharField(max_length=27)
    created_at = models.DateTimeField(auto_now_add=True)
    is_livemode = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=100)
    amount = models.IntegerField()
    source_id = models.CharField(max_length=29)
    is_captured = models.BooleanField(default=False)
    failure_message = models.CharField(default='No Error', max_length=200,
        help_text='Charge object failure message')
    failure_code = models.CharField(default='200', max_length=200, 
        help_text='Charge object failure code')
    error_http_status = models.CharField(default='200', max_length=4)
    error_type = models.CharField(default='None', max_length=200,
        help_text='The type of error returned. Can be invalid_request_error, api_error, or card_error')
    error_code = models.CharField(default='None', max_length=200,
        help_text='For card errors, a short string from amongst those listed on the right describing the kind of card error that occurred.')
    error_param = models.CharField(default='None', max_length=200,
        help_text='The parameter the error relates to if the error is parameter-specific.')
    error_message = models.CharField(default='None', max_length=300,
        help_text='A human-readable message giving more details about the error.')
    server_message = models.TextField(default='None', max_length=300,
        help_text='Message detailing internal server errors for debugging purposes')

    class Meta:
        ordering = ('created_at',)

    def __unicode__(self):
        return 'Charge attempt by {0} on {1} [{2}]'.format(
            self.email, self.created_at, 
            self.charge_id, self.status)


class Registration(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Other / I prefer not to disclose'),
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default=GENDER_CHOICES[0][0])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # student-specific
    is_student = models.BooleanField(default=False, verbose_name="Are you a student?")
    school = models.CharField(max_length=100, blank=True, verbose_name="Where do/did you go to school?")

    # contact
    email = models.EmailField()
    github = models.URLField(max_length=100, blank=True)
    linkedin = models.URLField(max_length=100, blank=True)

    # misc
    food_restrictions = models.TextField(max_length=100, default="None.",
        verbose_name="Do you have any allergies or food restrictions?")
    TSHIRT_SIZE_CHOICES = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'X-Large'),
    )
    tshirt_size = models.CharField(max_length=20, 
        choices=TSHIRT_SIZE_CHOICES,
        default=TSHIRT_SIZE_CHOICES[1][0])
    is_returning = models.BooleanField(default=False, verbose_name="Have you attended last year's event?")
    is_hacker = models.BooleanField(default=False, verbose_name="Is this your first hackathon?")

    # files
    resume = models.FileField(upload_to=get_resume_filename, blank=True, 
        help_text="Not required but this might reach our sponsors for targeted employment opportunities.")
    waiver = models.FileField(upload_to=get_waiver_filename, blank=True,
       help_text="Not required but it will save us some time during registration.")

    # payment
    charge = models.ForeignKey('ChargeAttempt', blank=True, null=True) #default=1)

    class Meta:
        ordering = ('last_name', 'first_name')

    def __unicode__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

