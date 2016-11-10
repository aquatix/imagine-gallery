# encoding: utf-8

from __future__ import absolute_import

import datetime
import logging
import os
import sys
from imagine.models import Collection, Directory, Image, ExifItem, Event
from PIL import Image as PILImage, ImageFile as PILImageFile, ExifTags
import exifread
from hashlib import md5
import imagehash

try:
    DEBUG
except NameError:
    DEBUG = True
    #DEBUG = False

logger = logging.getLogger('imagine')
logger.setLevel(logging.DEBUG)
#lh = logging.FileHandler('imagine_lib.log')
lh = logging.StreamHandler()
if DEBUG == True:
    lh.setLevel(logging.DEBUG)
else:
    lh.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
lh.setFormatter(formatter)
logger.addHandler(lh)


def get_filename(directory, filename):
    """Return (filename, extension) of the file in filename"""

    #newFilename, fileExtension = os.path.splitext(filename)[1][1:].strip()
    #print os.path.splitext(filename)[1][1:].strip()
    extension = os.path.splitext(filename)[1][1:].strip().lower()
    #print '[Info] {0} - {1}'.format(filename, fileExtension)

    new_filename = filename.replace(directory, '')
    return (new_filename, extension)


def save_jpg_exif(image, filename):
    """Fetch exif tags for the image Image object from the .jpg in filename"""
    # Open image file for reading (binary mode)
    f = open(filename, 'rb')

    # Return Exif tags
    exif = exifread.process_file(f)
    for k, v in exif.items():
        try:
            if 'thumbnail' in k.lower():
                logger.info('Skipping thumbnail exif item for {}'.format(filename))
                continue
            exif_item = ExifItem(
                    image=image,
                    key=k,
                    value_str=v
            )
            exif_item.save()
        except UnicodeDecodeError:
            logger.warning('Failed to save exif item %s due to UnicodeDecodeError' % k)


def save_cr2_exif(image, filename):
    """Fetch exif tags for the image Image object from the .cr2 raw file in filename"""
    logger.warning('cr2 metadata support not implemented yet')


def save_image_info(directory, the_image, filename, file_ext):
    """Create/update Image object from the image in filename"""

    the_image.filesize = os.stat(filename).st_size
    the_image.save()

    if file_ext not in Image.IMAGE_EXTENSIONS_RAW:
        try:
            image = PILImage.open(filename)
            the_image.image_hash = imagehash.average_hash(image)

            the_image.width = image.size[0]
            the_image.height = image.size[1]

            # Done with image info for now, save
            the_image.save()
        except IOError:
            logger.error('IOError opening ' + filename)

    if file_ext == 'jpg':
        save_jpg_exif(the_image, filename)
    elif file_ext == 'cr2':
        save_cr2_exif(the_image, filename)
    else:
        logger.warning('No supported extension found')

    #exif = {
    #        ExifTags.TAGS[k]: v
    #        for k, v in image._getexif().items()
    #        if k in ExifTags.TAGS
    #}
    #print(exif)
    #file = open(filename, 'r')
    #parser = PILImageFile.Parser()

    #while True:
    #	s = file.read(1024)
    #	if not s:
    #		break
    #	parser.feed(s)
    #image = parser.close()


    #print image.size

    #rw, rh = image.size()
    #print image.size

#	print image.fileName()
#	print image.magick()
#	print image.size().width()
#	print image.size().height()


#def update_collection(collection_name, collection_slug, images_dir, archive_dir):
def update_collection(collection):
    """ Creates a new image archive in archive_dir
    """
    #logger.debug('Writing archive to {0}'.format(archive_dir))
    #logger.debug('images_dir: {0}'.format(images_dir,''))

    #create_archive()
    #collection, created = Collection.get_or_create(name=collection_name, slug=collection_slug, base_dir=images_dir)
    #logger.debug('Collection created: ' + str(created))
    _walk_archive(collection)


def _walk_archive(collection):
    image_counter = 0
    skipped_counter = 0
    total_files = 0
    for dirname, dirnames, filenames in os.walk(collection.base_dir):
        this_dir = os.path.join(dirname, '')  # be sure to have trailing / and such
        logger.debug(this_dir)
        directory, created = Directory.objects.get_or_create(directory=this_dir, collection=collection)
        logger.debug('Directory created: ' + str(created))
        this_dir = this_dir.replace(collection.base_dir, '')
        for subdirname in dirnames:
            logger.debug('dir: {0}'.format(os.path.join(dirname, subdirname)))
        total_files = total_files + len(filenames)
        for filename in filenames:
            #print os.path.join(dirname, filename)
            this_file, this_file_ext = get_filename(collection.base_dir, os.path.join(dirname, filename))
            this_file = this_file.replace(this_dir, '')
            #logger.debug('ext: {0}'.format(this_file_ext)
            if this_file_ext in Image.IMAGE_EXTENSIONS:
                the_image, created = Image.objects.get_or_create(
                    directory=directory,
                    filename=filename,
                    file_ext=this_file_ext
                )
                if created:
                    # Only save if new image
                    save_image_info(directory, the_image, os.path.join(dirname, filename), this_file_ext)
                    logger.debug(the_image)
                    image_counter = image_counter + 1
                else:
                    skipped_counter = skipped_counter + 1
            else:
                logger.info('skipped {0}'.format(filename))

    logger.info('added {0} images to archive out of {1} total, skipped {2}'.format(image_counter, total_files, skipped_counter))

    return 42


def update_scaled_images(collection):
    """
    Iterate through the images in the Collection and generate resized versions of images
    that don't have those yet
    """
    images = collection.images()
