from django.db import models
import os, time

# Helpers
def get_resume_filename(instance, filename):
    return get_filename(instance, filename, directory='resumes')

def get_waiver_filename(instance, filename):
    return get_filename(instance, filename, directory='waivers')

def get_filename(instance, old_filename, directory=''):
    dirname = os.path.dirname(old_filename)
    # add time to differentiate between two registrees with the same first/last names
    suffix = time.strftime("%b--%d--%H-%M", time.gmtime(t))
    basename = '%s_%s_%s.pdf' % (last_name, first_name, suffix)
    filename = os.path.join(
        os.path.dirname(old_filename),
        directory,
        basename
        )
    return filename
    
class Registration(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'None'),
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default=GENDER_CHOICES[0][0])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # student-specific
    is_student = models.BooleanField(default=False)
    school = models.CharField(max_length=100, blank=True)

    # contact
    email = models.EmailField()
    github = models.URLField(max_length=100, blank=True)
    linkedin = models.URLField(max_length=100, blank=True)

    # misc
    food_restrictions = models.TextField(max_length=100, default="None.")
    TSHIRT_SIZE_CHOICES = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'X-Large'),
    )
    tshirt_size = models.CharField(max_length=20, 
        choices=TSHIRT_SIZE_CHOICES,
        default=TSHIRT_SIZE_CHOICES[1][0])
    is_returning = models.BooleanField(default=False)
    is_hacker = models.BooleanField(default=False)

    # files
    resume = models.FileField(upload_to=get_resume_filename, blank=True)
    waiver = models.FileField(upload_to=get_waiver_filename, blank=True)

    class Meta:
        ordering = ('last_name', 'first_name')

    def __unicode__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

