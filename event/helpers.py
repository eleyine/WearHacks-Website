def get_profile_pic_filename(instance, old_filename):
    import os
    filename, file_extension = os.path.splitext(old_filename)
    basename = '%s_%s.%s' % (instance.last_name, instance.first_name,
        file_extension)
    filename = os.path.join( 
        os.path.dirname(old_filename), 
        'profiles',
        basename
    )
    return filename