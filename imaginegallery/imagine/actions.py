import datetime
import logging
import os
import sys
import click
#from imagine_core import *
import imagine_core
from imagine_core import Collection, Directory, Image, ExifItem, Event
from utilkit import fileutil
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
            exif_item = ExifItem.create(
                    image=image,
                    key=k,
                    value_str=v
            )
        except UnicodeDecodeError:
            logger.warning('Failed to save exif item %s due to UnicodeDecodeError' % k)


def save_cr2_exif(image, filename):
    """Fetch exif tags for the image Image object from the .cr2 raw file in filename"""
    logger.warning('cr2 metadata support not implemented yet')


def save_image_info(directory, the_image, filename, file_ext):
    """Create/update Image object from the image in filename"""

    the_image.filesize = os.stat(filename).st_size
    the_image.save()

    if file_ext not in imagine_core.IMAGE_EXTENSIONS_RAW:
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


def update_collection(collection_name, collection_slug, images_dir, archive_dir):
    """ Creates a new image archive in archive_dir
    """
    logger.debug('Writing archive to {0}'.format(archive_dir))
    logger.debug('images_dir: {0}'.format(images_dir,''))

    #create_archive()
    collection, created = Collection.get_or_create(name=collection_name, slug=collection_slug, base_dir=images_dir)
    logger.debug('Collection created: ' + str(created))
    walk_archive(collection, images_dir, archive_dir)


def walk_archive(collection, images_dir, archive_dir):
    image_counter = 0
    skipped_counter = 0
    total_files = 0
    for dirname, dirnames, filenames in os.walk(images_dir):
        this_dir = os.path.join(dirname, '')	# be sure to have trailing / and such
        logger.debug(this_dir)
        directory, created = Directory.get_or_create(directory=this_dir, collection=collection)
        logger.debug('Directory created: ' + str(created))
        this_dir = this_dir.replace(images_dir, '')
        for subdirname in dirnames:
            logger.debug('dir: {0}'.format(os.path.join(dirname, subdirname)))
        total_files = total_files + len(filenames)
        for filename in filenames:
            #print os.path.join(dirname, filename)
            this_file, this_file_ext = get_filename(images_dir, os.path.join(dirname, filename))
            this_file = this_file.replace(this_dir, '')
            #logger.debug('ext: {0}'.format(this_file_ext)
            if this_file_ext in imagine_core.IMAGE_EXTENSIONS:
                the_image, created = Image.get_or_create(
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


## Main program
@click.group()
def cli():
    """
    imagine image archive
    """
    pass


@cli.command()
@click.option('-i', '--inputdir', prompt='Input/source directory path', help='Input/source directory path')
@click.option('-a', '--archivedir', prompt='Archive/target directory path', help='Archive/target directory path')
def update_archive(inputdir, archivedir):
    print('Updating or creating archive in {0} from source at {1}'.format(archivedir, inputdir))

    # expand directories and appending / if needed
    inputdir = os.path.join(inputdir,'')
    archivedir = os.path.join(archivedir,'')

    fileutil.ensure_dir_exists(archivedir)

    print 'Scanning {0}'.format(inputdir)

    db_file = os.path.join(archivedir, 'imagine_cli.db')
    should_create = True
    print db_file
    if os.path.exists(db_file):
        should_create = False

    imagine_core.init_db(db_file)
    if should_create:
        imagine_core.create_archive()

    update_collection('test', 'test-slug', inputdir, archivedir)


if __name__ == '__main__':
    """
    imagine is ran standalone
    """
    cli()
