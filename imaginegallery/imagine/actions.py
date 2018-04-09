# encoding: utf-8

from __future__ import absolute_import

import logging
import os
from django.conf import settings
from imagine.models import Collection, Directory, Image, ImageMeta, PhotoSize, ExifItem
from imagine import util
from PIL import Image as PILImage, ImageFile as PILImageFile, ExifTags
from datetime import datetime
import exifread
import imagehash
import json
import pytz
import requests

try:
    DEBUG = settings.DEBUG
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


def save_image_geo_location(image):
    """Queries Google's GEO API for the location of this Image"""

    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}'.format(image.geo_lat, image.geo_lon))
    json_data = json.loads(response.text)

    # Pick the first one, this is generally the most specific result
    # https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding
    if not json_data:
        logger.warning('No geo found for %s', str(image))
        return
    image.geo_formatted_address = json_data['results'][0]['formatted_address']
    for component in json_data['results'][0]['address_components']:
        if 'route' in component['types']:
            # 'Street'
            image.geo_route = component['long_name']
        elif 'postal_code' in component['types']:
            image.geo_postal_code = component['long_name']
        elif 'locality' in component['types']:
            image.geo_city = component['long_name']
        elif 'administrative_area_level_1' in component['types']:
            image.geo_administrative_area_level_1 = component['long_name']
        elif 'geo_administrative_area_level_2' in component['types']:
            image.geo_administrative_area_level_2 = component['long_name']
        elif 'country' in component['types']:
            image.geo_country = component['long_name']
            image.geo_country_code = component['short_name']

    image.save()


def save_jpg_exif(image, filename):
    """Fetch exif tags for the image Image object from the .jpg in filename"""
    # Open image file for reading (binary mode)
    f = open(filename, 'rb')

    datetime_taken = None
    geo = {}

    # Return Exif tags
    exif = exifread.process_file(f)
    for k, v in exif.items():
        try:
            if 'thumbnail' in k.lower():
                #logger.debug('Skipping thumbnail exif item for %s', filename)
                continue
            exif_item = ExifItem(
                    image=image,
                    key=k,
                    value_str=v
            )
            exif_item.save()
            if k == 'EXIF DateTimeOriginal':
                datetime_taken = str(v)
            if k == 'GPS GPSLatitude':
                geo['GPS GPSLatitude'] = v
            if k == 'GPS GPSLatitudeRef':
                geo['GPS GPSLatitudeRef'] = v
            if k == 'GPS GPSLongitude':
                geo['GPS GPSLongitude'] = v
            if k == 'GPS GPSLongitudeRef':
                geo['GPS GPSLongitudeRef'] = v
        except UnicodeDecodeError:
            logger.warning('Failed to save exif item %s due to UnicodeDecodeError', k)
    return datetime_taken, geo


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
            the_image.image_hash = imagehash.dhash(image)

            the_image.width = image.size[0]
            the_image.height = image.size[1]

            # Done with image info for now, save
            the_image.save()
        except IOError:
            logger.error('IOError opening %s', filename)

    exif_datetime_taken = None

    if file_ext == 'jpg':
        exif_datetime_taken, geo_exif_items = save_jpg_exif(the_image, filename)
    elif file_ext == 'cr2':
        save_cr2_exif(the_image, filename)
    else:
        logger.warning('No supported extension found')

    #the_image.file_modified = datetimeutil.unix_to_python(os.path.getmtime(filename))
    the_image.file_modified = datetime.fromtimestamp(float((os.path.getmtime(filename))), tz=pytz.utc)

    if exif_datetime_taken:
        #the_image.exif_modified = datetimeutil.load_datetime(exif_datetime_taken, '%Y:%m:%d %H:%M:%S')
        the_image.exif_modified = util.load_datetime(exif_datetime_taken, '%Y:%m:%d %H:%M:%S').replace(tzinfo=pytz.utc)
        the_image.filter_modified = the_image.exif_modified
    else:
        the_image.filter_modified = the_image.file_modified

    try:
        if geo_exif_items:
            lat, lon = util.get_exif_location(geo_exif_items)
            the_image.geo_lat = lat
            the_image.geo_lon = lon
            # TODO: create config item to enable/disable geo lookups
            # Do request to http://maps.googleapis.com/maps/api/geocode/xml?latlng=53.244921,-2.479539&sensor=true
            save_image_geo_location(the_image)
    except UnboundLocalError:
        # No geo data
        pass

    the_image.save()

    # TODO: update exif highlights fields from EXIF tags
    # exifhighlights = self.get_exif_highlights()

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

    for directory in directory_list:
        # If relative_path is empty, it's the root of the collection, otherwise assign a parent
        if not directory.relative_path:
            directory.parent_directory = None  # root of Collection
            directory.save()
        else:
            parent_directory_path = os.path.abspath(os.path.join(directory.directory, os.pardir)) + '/'
            directory.parent_directory = Directory.objects.get(directory=parent_directory_path)
            directory.save()


def _walk_archive(collection):
    image_counter = 0
    skipped_counter = 0
    total_files = 0
    created_dirs = 0
    for dirname, _dirnames, filenames in os.walk(collection.base_dir):
        this_dir = os.path.join(dirname, '')  # be sure to have trailing / and such
        full_dir = this_dir
        #logger.debug(this_dir)
        this_dir = this_dir.replace(collection.base_dir, '')
        if this_dir[0] == '/':
            this_dir = this_dir[1:]
        if this_dir and this_dir[-1] == '/':
            this_dir = this_dir[:-1]
        directory, created = Directory.objects.get_or_create(directory=full_dir, relative_path=this_dir, collection=collection)
        logger.debug('Directory %s created: %s', full_dir, str(created))
        if created:
            created_dirs = created_dirs + 1
        #for subdirname in dirnames:
        #    logger.debug('dir: %s', os.path.join(dirname, subdirname))
        total_files = total_files + len(filenames)
        for filename in filenames:
            #print os.path.join(dirname, filename)
            this_file, this_file_ext = get_filename(collection.base_dir, os.path.join(dirname, filename))
            this_path = os.path.dirname(this_file)
            this_file = this_file.replace(this_dir, '')
            #logger.debug('ext: %s', this_file_ext)
            if this_file_ext in Image.IMAGE_EXTENSIONS:
                the_image, created = Image.objects.get_or_create(
                    collection=collection,
                    directory=directory,
                    filename=filename,
                    file_ext=this_file_ext,
                    file_path=this_path,
                )
                if created:
                    # Only save if new image
                    save_image_info(the_image, os.path.join(dirname, filename), this_file_ext)
                    logger.info('created Image for %s', the_image)
                    image_counter = image_counter + 1
                else:
                    skipped_counter = skipped_counter + 1
                    #logger.debug('skipped Image for %s', the_image)
                the_image_hash, created = ImageMeta.objects.get_or_create(image_hash=the_image.image_hash)
            else:
                #logger.info('skipped %s', filename)
                pass

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
    util.ensure_dir_exists(filename_base)
    variant = '_{}-{}.{}'.format(width, height, image.file_ext)
    if os.path.isfile(filename_base + variant):
        #logger.debug('Skipping resize for existing %s%s', filename_base, variant)
        return

    logger.info('resizing into %s', filename_base + variant)
    # TODO: be more clever with the config
    if width == 0:
        raise Exception('width can not be zero')
    if height == 0:
        raise Exception('height can not be zero')
    try:
        im = PILImage.open(image.get_filepath())
        im.thumbnail((width, height))
        if image.file_ext == 'jpg' or image.file_ext == 'jpeg':
            if width >= settings.EXIF_COPY_THRESHOLD or height >= settings.EXIF_COPY_THRESHOLD:
                # If variant is larger than the set threshold, copy EXIF tags
                # Smaller variants effectively get EXIF stripped so resulting files are smaller
                # (good for thumbnails)
                try:
                    exif = im.info['exif']
                    im.save(filename_base + variant, 'JPEG', exif=exif)
                except KeyError:
                    # No EXIF found, save normally
                    im.save(filename_base + variant, 'JPEG')
            else:
                im.save(filename_base + variant, 'JPEG')
        elif image.file_ext == 'png':
            im.save(filename_base + variant, 'PNG')
    except IOError:
        logger.info('Cannot create %dx%d variant for %s', width, height, image)


def clean_collection(collection):
    """
    Iterate through the images in the Collection and remove those that don't exist
    on disk anymore
    """
    images = collection.images()
    number_purged = 0
    for image in images:
        if not os.path.isfile(image.get_filepath()):
            logger.info('Removing Image %s from collection %s', image.get_filepath(), collection)
            image.delete()
            number_purged = number_purged + 1
    return number_purged


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


def update_everything():
    """
    Iterate through all Collection's, update_collection, remove stale images and scale images
    """
    collections = Collection.objects.all()
    for collection in collections:
        update_collection(collection)
        clean_collection(collection)
        update_scaled_images(collection)
