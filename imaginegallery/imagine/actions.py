# encoding: utf-8

from __future__ import absolute_import

import logging
import os
from imagine.models import Directory, Image, ImageMeta, PhotoSize, ExifItem
from PIL import Image as PILImage, ImageFile as PILImageFile, ExifTags
import exifread
import imagehash
from utilkit import fileutil, datetimeutil

try:
    DEBUG
except NameError:
    DEBUG = True
    #DEBUG = False

logger = logging.getLogger('imagine')
logger.setLevel(logging.DEBUG)
#lh = logging.FileHandler('imagine_lib.log')
lh = logging.StreamHandler()
if DEBUG:
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

    datetime_taken = None

    # Return Exif tags
    exif = exifread.process_file(f)
    for k, v in exif.items():
        try:
            if 'thumbnail' in k.lower():
                logger.info('Skipping thumbnail exif item for %s', filename)
                continue
            exif_item = ExifItem(
                    image=image,
                    key=k,
                    value_str=v
            )
            exif_item.save()
            if k == 'EXIF DateTimeOriginal':
                datetime_taken = str(v)
        except UnicodeDecodeError:
            logger.warning('Failed to save exif item %s due to UnicodeDecodeError', k)
    return datetime_taken


def save_cr2_exif(image, filename):
    """Fetch exif tags for the image Image object from the .cr2 raw file in filename"""
    logger.warning('cr2 metadata support not implemented yet')


def save_image_info(the_image, filename, file_ext):
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
            logger.error('IOError opening %s', filename)

    datetime_taken = None

    if file_ext == 'jpg':
        datetime_taken = save_jpg_exif(the_image, filename)
    elif file_ext == 'cr2':
        save_cr2_exif(the_image, filename)
    else:
        logger.warning('No supported extension found')

    if datetime_taken:
        the_image.exif_modified = datetimeutil.load_datetime(datetime_taken, '%Y:%m:%d %H:%M:%S')
        the_image.filter_modified = the_image.exif_modified
    the_image.save()

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
    #logger.debug('Writing archive to %s', archive_dir)
    #logger.debug('images_dir: %s', images_dir,'')

    #create_archive()
    #collection, created = Collection.get_or_create(name=collection_name, slug=collection_slug, base_dir=images_dir)
    #logger.debug('Collection created: %s', str(created))
    _walk_archive(collection)


def _update_directory_parents(collection):
    """
    Correctly assign parent directories to the various directory objects
    """
    directory_list = Directory.objects.filter(collection=collection).order_by('directory')
    print(directory_list)

    root_directory = None
    previous_directory = None
    previous_root = None
    for directory in directory_list:
        # If relative_path is empty, it's the root of the collection, otherwise assign a parent
        if not directory.relative_path:
            directory.parent_directory = None  # root of Collection
            directory.save()
            previous_root = directory
            root_directory = directory
        else:
            if previous_directory:
                common_prefix = os.path.commonprefix([directory.relative_path, previous_directory.relative_path])
                if not common_prefix:
                    directory.parent_directory = root_directory
                    directory.save()
                    previous_root = directory
                elif common_prefix[-1] == '/':
                    # Directory's share the same root
                    directory.parent_directory = previous_root
                    directory.save()
                else:
                    # directory is a child of previous_directory
                    directory.parent_directory = previous_directory
                    directory.save()

        previous_directory = directory


def _walk_archive(collection):
    image_counter = 0
    skipped_counter = 0
    total_files = 0
    created_dirs = 0
    for dirname, dirnames, filenames in os.walk(collection.base_dir):
        this_dir = os.path.join(dirname, '')  # be sure to have trailing / and such
        full_dir = this_dir
        logger.debug(this_dir)
        this_dir = this_dir.replace(collection.base_dir, '')
        if this_dir[0] == '/':
            this_dir = this_dir[1:]
        if this_dir and this_dir[-1] == '/':
            this_dir = this_dir[:-1]
        directory, created = Directory.objects.get_or_create(directory=full_dir, relative_path=this_dir, collection=collection)
        logger.debug('Directory created: %s', str(created))
        if created:
            created_dirs = created_dirs + 1
        for subdirname in dirnames:
            logger.debug('dir: %s', os.path.join(dirname, subdirname))
        total_files = total_files + len(filenames)
        for filename in filenames:
            #print os.path.join(dirname, filename)
            this_file, this_file_ext = get_filename(collection.base_dir, os.path.join(dirname, filename))
            this_path = os.path.dirname(this_file)
            this_file = this_file.replace(this_dir, '')
            #logger.debug('ext: %s', this_file_ext)
            if this_file_ext in Image.IMAGE_EXTENSIONS:
                the_image, created = Image.objects.get_or_create(
                    directory=directory,
                    filename=filename,
                    file_ext=this_file_ext,
                    file_path=this_path,
                )
                if created:
                    # Only save if new image
                    save_image_info(the_image, os.path.join(dirname, filename), this_file_ext)
                    logger.debug(the_image)
                    logger.info('created Image for %s', the_image)
                    image_counter = image_counter + 1
                else:
                    skipped_counter = skipped_counter + 1
                    logger.debug('skipped Image for %s', the_image)
                the_image_hash, created = ImageMeta.objects.get_or_create(image_hash=the_image.image_hash)
                if created:
                    logger.debug('created ImageMeta for hash %s', the_image_hash.image_hash)
                else:
                    logger.debug('skipped ImageMeta for hash %s', the_image_hash.image_hash)
            else:
                logger.info('skipped %s', filename)

    logger.info('added %d images to archive out of %d total, skipped %d; created %d directories', image_counter, total_files, skipped_counter, created_dirs)

    #if created_dirs:
    _update_directory_parents(collection)

    return image_counter, total_files, skipped_counter


def scale_image(image_id, destination_dir, width, height, crop=False):
    """
    Create scaled versions of the Image with image_id
    """
    image = Image.objects.get(pk=image_id)
    if not image.image_hash:
        logger.info('No hash found for Image with pk %d', image.pk)
        return
    filename_base = os.path.join(destination_dir, image.image_hash[:2], image.image_hash)
    fileutil.ensure_dir_exists(filename_base)
    variant = '_{}-{}.jpg'.format(width, height)
    if os.path.isfile(filename_base + variant):
        logger.debug('Skipping resize for existing %s%s', filename_base, variant)

    print('resizing into {}'.format(filename_base + variant))
    # TODO: be more clever with the config
    max_size = max(width, height)
    try:
        im = PILImage.open(image.get_filepath())
        im.thumbnail((max_size, max_size), PILImage.ANTIALIAS)
        # TODO: copy EXIF info
        im.save(filename_base + variant, 'JPEG')
    except IOError:
        logger.info('Cannot create %dx%d variant for %s', width, height, image)


def update_scaled_images(collection):
    """
    Iterate through the images in the Collection and generate resized versions of images
    that don't have those yet
    """
    images = collection.images()
    variants = PhotoSize.objects.all()
    if len(variants) == 0:
        logger.info('No size variants defined, configure some PhotoSizes')
        return
    for image in images:
        for variant in variants:
            scale_image(image.pk, collection.archive_dir, variant.width, variant.height, variant.crop_to_fit)
