from django.db import models

class ContentTypeRestrictedFileField(models.FileField):
    """
    Source http://nemesisdesign.net/blog/coding/django-filefield-content-type-size-validation/
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):        
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        
        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep file size under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass        
            
        return data

class PDFFileField(ContentTypeRestrictedFileField):
    '''
    Validates that the file is a PDF
    '''
    def __init__(self, *args, **kwargs):
        super(PDFFileField, self).__init__(content_types = ['application/pdf'], *args, **kwargs)

    def clean(self, *args, **kwargs):
        from pyPdf import PdfFileReader
        data = super(PDFFileField, self).clean(*args, **kwargs)

        file = data.file

        try:
            PdfFileReader(file)
        except Exception as e:
            raise forms.ValidationError(_('Not a PDF File'))

        return data