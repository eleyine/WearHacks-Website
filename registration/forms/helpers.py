from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.utils import ValidationError
    
class PDFField(forms.FileField):
    """
    Modified from https://djangosnippets.org/snippets/1189/
    """
    default_error_messages = {
        'invalid': _(u"No file was submitted."), #" Check the encoding type on the form."),
        'missing': _(u"No file was submitted."),
        'empty': _(u"The submitted file is empty."),
        'not_valid': _(u"Upload a valid document. The file you uploaded appears to be corrupted."),
        'not_pdf': _(u"Not a PDF file."),
        'file_size': _(u"Please keep file size under %(max_file_size)s. Current filesize %(current_file_size)s"),
        'sever_error': _(u"There was an issue uploading your file. Try to submit again."),

    }

    required = False
    max_upload_size = 2621440 # 2MB
    content_types = ['application/pdf']

    def clean(self, data, initial=None):
        super(forms.FileField, self).clean(initial or data)
        if not data:
            return data
      
        file = data.file
        try:
            if not file.readable:
                raise ValidationError(self.error_messages['not_valid'])
            if data._size > self.max_upload_size:
                raise forms.ValidationError(self.error_messages['file_size'],
                    params = {
                     max_file_size: filesizeformat(self.max_upload_size), 
                     current_file_size: filesizeformat(data._size)
                    })
            try:
                from pyPdf import PdfFileReader
                PdfFileReader(file)
            except Exception as e:
                print str(e)
                raise ValidationError(self.error_messages['not_pdf'])
        except ValidationError, e:
            raise e
        except Exception, e:
            print str(e)
            raise forms.ValidationError(self.error_messages['sever_error'])
        return data