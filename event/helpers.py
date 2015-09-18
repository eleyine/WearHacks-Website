import os

def get_profile_pic_filename(instance, old_filename):
    filename, file_extension = os.path.splitext(old_filename)
    basename = '%s_%s.%s' % (instance.last_name, instance.first_name,
        file_extension)
    filename = os.path.join( 
        os.path.dirname(old_filename), 
        'profiles',
        basename
    )
    return filename

def get_image_filename(instance, old_filename):
    folder = ''
    if hasattr(instance, 'IMAGE_FOLDER'):
        folder = instance.IMAGE_FOLDER

    filename = os.path.join( 
        os.path.dirname(old_filename), 
        folder,
        old_filename
    )
    return filename
