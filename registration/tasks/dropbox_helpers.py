#!/usr/bin/env python
"""mysql-backup.py: Backups up all MySQL databases and sends them to Dropbox"""

import gzip
import zipfile
import os
import re
import socket
import sys
import time
import shutil
import errno

try:
    from dropbox import client, rest, session
except ImportError:
    sys.exit("Need Dropbox! (https://www.dropbox.com/developers/reference/sdk)")

try:
    from hurry.filesize import size
except ImportError:
    sys.exit("Need hurry.filesize! (http://pypi.python.org/pypi/hurry.filesize/)")

# - - - - - - - - - - CONFIG OPTIONS - - - - - - - - - - #

from django.conf import settings

try:
    from settings import (
        DROPBOX_APP_KEY,
        DROPBOX_APP_SECRET,
        DROPBOX_ACCESS,
        DROPBOX_FOLDER,
        DROPBOX_SERVER_FOLDER,
        DROPBOX_TOKEN_FILE,
        DROPBOX_TO_BACKUP,
        DROPBOX_OPTION_GZIP,
        DROPBOX_OPTION_USE_HOST,
        DROPBOX_OPTION_ZIP_FOLDERS,
        )
except ImportError, e:
    sys.exit("%s\nPlease update private.py, see example_private_settings.py" % (e))


# - - - - - - - - - - END OF CONFIG OPTIONS! - - - - - - - - - - #

# Directory to work in (include trailing slash)
# Will be created if it doesn't exist.
TMP_FOLDER = os.path.join(DROPBOX_SERVER_FOLDER, 'tmp/')

def _copy(src, dst):
    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def _get_files_recursively(folder):
    if not os.path.isdir(folder):
        raise Exception('%s is not a folder' % (folder))

    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for f in filenames:
            matches.append(os.path.join(root, f))
    return matches

def zipdir(path, ziph, root_to_remove=None):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            if root_to_remove:
                arcname = os.path.join(
                    root.replace(root_to_remove, ''),
                    file)
                ziph.write(os.path.join(root, file), arcname=arcname)
            else:
                ziph.write(os.path.join(root, file))

def get_timestamp():
    """Returns a MySQL-style timestamp from the current time"""
    return time.strftime("%Y-%m-%d %H:%M:%S")

def do_mysql_backup(tmp_file):
    """Backs up the MySQL server (all DBs) to the specified file"""
    os.system("%s -u %s -p\"%s\" -h %s -P %d --opt --all-databases > %s" % (MYSQL_DUMP_PATH, MYSQL_ROOT_USER, MYSQL_ROOT_PASS, MYSQL_HOSTNAME, MYSQL_PORT, TMP_FOLDER + tmp_file))

def connect_to_dropbox():
    """Authorizes the app with Dropbox. Returns False if we can't connect"""

    access_token = ''

    # Do we have access tokens?
    while len(access_token) == 0:
        try:
            token_file = open(DROPBOX_TOKEN_FILE, 'r')
        except IOError:
            # Re-build the file and try again, maybe?
            get_new_dropbox_tokens()
            token_file = open(DROPBOX_TOKEN_FILE, 'r')
        
        access_token = token_file.read()        
        token_file.close()

    # Hopefully now we have token_key and token_secret...
    dropbox_client = client.DropboxClient(access_token)

    # Double-check that we've logged in
    try:
        dropbox_info = dropbox_client.account_info()
    except:
        # If we're at this point, someone probably deleted this app in their DB 
        # account, but didn't delete the tokens file. Clear everything and try again.
        os.unlink(DROPBOX_TOKEN_FILE)
        connect_to_dropbox()    # Who doesn't love a little recursion?

    return (dropbox_client, dropbox_info)


def get_new_dropbox_tokens():
    """Helps the user auth this app with Dropbox, and stores the tokens in a file"""

    flow = client.DropboxOAuth2FlowNoRedirect(DROPBOX_APP_KEY, DROPBOX_APP_SECRET)
    authorize_url = flow.start()

    print "Looks like you haven't allowed this app to access your Dropbox account yet!"
    print "1. Visit " + authorize_url
    print "2. Click \"Allow\" (you might have to log in first)"
    print "3. Copy the authorization code"

    code = raw_input("Enter authorization code here: ").strip()
    access_token, user_id = flow.finish(code)
    
    token_file = open(DROPBOX_TOKEN_FILE, 'w')
    token_file.write(access_token)
    token_file.close()

class StdoutLogger(object):
    def warn(self):
        print s
    def error(self):
        print s
    def info(self):
        print s
    def debug(self):
        print s

def backup(logger=None):
    if not logger:
        logger = StdoutLogger()

    # Are we prepending hostname to filename?
    hostname = (socket.gethostname()) if(DROPBOX_OPTION_USE_HOST == True) else ''

    # Make dir for hostname in tmp dir if needed...
    if hostname:
        tmp_folder = os.path.join(TMP_FOLDER, hostname, 'backup-' + get_timestamp())
    else:
        tmp_folder = os.path.join(TMP_FOLDER, 'backup-' + get_timestamp())

    # Make tmp dir if needed...  
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    # MYSQL_TMP_FILE  = re.sub('[\\/:\*\?"<>\|\ ]', '-', hostname + 'backup-' + get_timestamp()) + '.sql'

    # Got final filename, continue on...
    logger.info("Connecting to Dropbox...")
    dropbox_client, dropbox_info = connect_to_dropbox()

    logger.info("Connected to Dropbox as " + dropbox_info['display_name'])
    logger.info('=' * 20)
    for file_or_folder_to_backup in DROPBOX_TO_BACKUP:
        if not os.path.exists(file_or_folder_to_backup):
            logger.warn('WARNING: %s does not exist' % (file_or_folder_to_backup))
            continue

        logger.info('\nBacking up: %s' % (file_or_folder_to_backup))
        # if f is folder, do gzip...
        file_or_folder_basename = os.path.basename(file_or_folder_to_backup)
        # file_or_folder_basename = re.sub('[\\/:\*\?"<>\|\ ]', '-', file_or_folder_basename + '-backup-' + get_timestamp())

        tmp_file_or_folder = os.path.join(tmp_folder, file_or_folder_basename)
        _copy(file_or_folder_to_backup, tmp_file_or_folder)

        tmp_files = []

        if os.path.isdir(tmp_file_or_folder):
            if DROPBOX_OPTION_ZIP_FOLDERS: 
                logger.info("Zipping folder %s" % (tmp_file_or_folder))
                zip_fn = tmp_file_or_folder + '-archive.zip'
                # zip_fn = zip_fn.replace(tmp_folder, '')
                zipf = zipfile.ZipFile(zip_fn, 'w')
                zipdir(tmp_file_or_folder, zipf, root_to_remove=tmp_file_or_folder)

                # shutil.make_archive(os.path.basename(tmp_file_or_folder), "zip", tmp_file_or_folder)
                # zipf.write()
                zipf.close()
                tmp_files.append(zip_fn)
            else:
                tmp_folder_matches = _get_files_recursively(tmp_file_or_folder)
                tmp_files.extend(tmp_folder_matches)
        else:
            tmp_files.append(tmp_file_or_folder)

        if DROPBOX_OPTION_GZIP:
            new_tmp_files = []

            logger.debug("GZip enabled")
            for tmp_filename in tmp_files:
                old_size = size(os.path.getsize(tmp_filename))
                logger.info("Compressing %s (Filesize: %s)" % (
                    tmp_filename,
                    old_size)
                )
                gz_filename = tmp_filename + '.gz'
                # Write uncompressed file to gzip file:
                tmp_file = open(tmp_filename, 'rb')
                gz_file  = gzip.open(gz_filename, 'wb')
                gz_file.writelines(tmp_file)

                tmp_file.close()
                gz_file.close()

                # Delete uncompressed TMP_FILE, set to .gz
                os.remove(tmp_filename)

                # Tell the user how big the compressed file is:
                logger.info("      %s -> %s" % (
                    old_size,
                    size(os.path.getsize(gz_filename)))
                )
                new_tmp_files.append(gz_filename)

            tmp_files = new_tmp_files

        for tmp_filename in tmp_files:
            tmp_file = open(tmp_filename, 'rb')
            tmp_size = os.path.getsize(tmp_filename)

            logger.info("Uploading %s (size:%s) to Dropbox..." % (tmp_file, size(tmp_size)))
            uploader = dropbox_client.get_chunked_uploader(tmp_file, tmp_size)

            while uploader.offset < tmp_size:
                try:
                    upload = uploader.upload_chunked(1024 * 1024)
                except rest.ErrorResponse, e:
                    logger.error("Error: %d %s" % (e.errno, e.strerror))
                    pass
            dropbox_dst = tmp_filename.replace(TMP_FOLDER, DROPBOX_FOLDER)

            try:
                uploader.finish(dropbox_dst)
            except Exception, e:
                logger.info(e)
            tmp_file.close()

            logger.info("Uploaded as \"%s\" size: %s" % (dropbox_dst, size(tmp_size)))
        logger.info('-' * 20)
    logger.info("Cleaning up...")
    logger.debug("Deleting %s" % (tmp_folder))
    if os.path.exists(tmp_folder):
        if os.path.isdir(tmp_folder):
            shutil.rmtree(tmp_folder)
        else:
            os.remove(tmp_folder)