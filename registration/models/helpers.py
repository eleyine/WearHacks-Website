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

from django.core.files.storage import FileSystemStorage
from django.conf import settings

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Found at http://djangosnippets.org/snippets/976/

        This file storage solves overwrite on upload problem. Another
        proposed solution was to override the save method on the model
        like so (from https://code.djangoproject.com/ticket/11663):

        def save(self, *args, **kwargs):
            try:
                this = MyModelName.objects.get(id=self.id)
                if this.MyImageFieldName != self.MyImageFieldName:
                    this.MyImageFieldName.delete()
            except: pass
            super(MyModelName, self).save(*args, **kwargs)
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name