import datetime, os
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Helpers
def get_resume_filename(instance, filename):
    return get_filename(instance, filename, directory='resumes')

def get_waiver_filename(instance, filename):
    return get_filename(instance, filename, directory='waivers')

def get_ticket_filename(instance, old_filename):
    basename = '%s.pdf' % (instance.order_id)
    filename = os.path.join(os.path.dirname(old_filename), 
        'tickets', basename )
    return filename

def get_qrcode_filename(instance, old_filename):
    basename = '%s.png' % (instance.order_id)
    filename = os.path.join(os.path.dirname(old_filename), 
        'qrcodes', basename )
    return filename


def get_filename(instance, old_filename, directory=''):
    # add time to differentiate between two registrees with the same first/last names
    suffix = datetime.datetime.now().strftime("__%m-%d_%H-%M")
    basename = '%s_%s_%s.pdf' % (instance.last_name, instance.first_name, suffix)
    filename = os.path.join(
        os.path.dirname(old_filename),
        directory,
        basename
        )
    return filename

def validate_true(value):
    if not value:
        raise ValidationError(_('This field must be checked'))