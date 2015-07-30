import datetime, os

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

def validate_true(value):
    if not value:
        raise ValidationError('This field must be checked')