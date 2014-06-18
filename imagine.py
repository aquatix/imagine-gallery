import datetime
import logging
import os
import sys
from peewee import *
from PIL import Image as PILImage, ImageFile as PILImageFile, ExifTags
import exifread

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

DBVERSION = 1
DATABASE = 'imagine.db' # default value
IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'cr2']
IMAGE_EXTENSIONS_RAW = ['cr2']

database = SqliteDatabase(DATABASE)
# database = None


# == imagine models

class BaseModel(Model):
    class Meta:
        database = database


class Collection(BaseModel):
    name = CharField()
    base_dir = CharField()

    added_at = DateTimeField(default=datetime.datetime.now())

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.base_dir)


class Directory(BaseModel):
    directory = CharField()
    collection = ForeignKeyField(Collection)

    added_at = DateTimeField(default=datetime.datetime.now())

    def get_filepath(self, filename):
        return '{0}/{1}'.format(self.directory, filename)

    def __unicode__(self):
        return self.directory


class Image(BaseModel):
    directory = ForeignKeyField(Directory, related_name='parent')
    filename = CharField()
    file_ext = CharField()
    filetype = CharField(null=True)
    filesize = IntegerField(default=-1)
    file_modified = DateTimeField(null=True)

    added_at = DateTimeField(default=datetime.datetime.now())
    description = TextField(default='')
    is_visible = BooleanField(default=True)

    width = IntegerField(default=-1)
    height = IntegerField(default=-1)

    image_hash = CharField(null=True)
    thumb_hash = CharField(null=True)

    class Meta:
        order_by = ('filename',)


    def get_filepath(self):
        dirname = Directory.select().where(
                Directory = self.directory
        )
        return '{0}/{1}'.format(dirname, self.filename)

    def __unicode__(self):
        return self.get_filepath(self)


class ExifItem(BaseModel):
    image = ForeignKeyField(Image)
    key = CharField()
    value_str = CharField(null=True)
    value_int = IntegerField(null=True)
    value_float = FloatField(null=True)

    def get_value(as_type='str'):
        # TODO: be able to return _int or _float
        return value_str


def create_archive():
    database.connect()
    Collection.create_table()
    Directory.create_table()
    Image.create_table()
    ExifItem.create_table()


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
            logger.warning('Failed to save %s due to UnicodeDecodeError' % k)


def save_cr2_exif(image, filename):
    """Fetch exif tags for the image Image object from the .cr2 raw file in filename"""
    logger.warning('cr2 metadata support not implemented yet')


def save_image_info(directory, the_image, filename, file_ext):
    """Create/update Image object from the image in filename"""

    the_image.filesize = os.stat(filename).st_size
    the_image.save()

    if file_ext not in IMAGE_EXTENSIONS_RAW:
        image = PILImage.open(filename)

        the_image.width = image.size[0]
        the_image.height = image.size[1]

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


def update_collection(collection_name, images_dir, archive_dir):
    """ Creates a new image archive in archive_dir
    """
    logger.debug('Writing archive to {0}'.format(archive_dir))
    logger.debug('images_dir: {0}'.format(images_dir,''))

    #create_archive()
    collection = Collection.get_or_create(name=collection_name, base_dir=images_dir)
    walk_archive(collection, images_dir, archive_dir)


def walk_archive(collection, images_dir, archive_dir):
    image_counter = 0
    total_files = 0
    for dirname, dirnames, filenames in os.walk(images_dir):
        this_dir = os.path.join(dirname, '')	# be sure to have trailing / and such
        logger.debug(this_dir)
        directory = Directory.create(directory=this_dir, collection=collection)
        this_dir = this_dir.replace(images_dir, '')
        for subdirname in dirnames:
            logger.debug('dir: {0}'.format(os.path.join(dirname, subdirname)))
        total_files = total_files + len(filenames)
        for filename in filenames:
            #print os.path.join(dirname, filename)
            this_file, this_file_ext = get_filename(images_dir, os.path.join(dirname, filename))
            this_file = this_file.replace(this_dir, '')
            #logger.debug('ext: {0}'.format(this_file_ext)
            if this_file_ext in IMAGE_EXTENSIONS:
                the_image = Image.get_or_create(
                    directory=directory,
                    filename=filename,
                    file_ext=this_file_ext
                )
                save_image_info(directory, the_image, os.path.join(dirname, filename), this_file_ext)
                image_counter = image_counter + 1
            else:
                logger.info('skipped {0}'.format(filename))

    logger.info('added {0} images to archive out of {1} total'.format(image_counter, total_files))

    return 42

