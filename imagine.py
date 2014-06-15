import datetime

import argparse
import os
import sqlite3
import sys
from socket import gethostname
from PIL import Image as PILImage, ImageFile as PILImageFile
from peewee import *

DBVERSION = 1
DATABASE = 'imagine.db' # default value
IMAGEEXTENSIONS = ['jpg', 'jpeg', 'png', 'cr2']

DEBUG = True
#DEBUG = False

# database = SqliteDatabase(DATABASE)
database = None


def prt(messageType, message):
	if DEBUG == False:
		return

	if messageType == 'i':
		print '[Info] {0}'.format(message)
	elif messageType == 'e':
		print '[Error] {0}'.format(message)
	elif messageType == 'd':
		print '[Debug] {0}'.format(message)


class BaseModel(Model):
    class Meta:
        database = database


class Collection(BaseModel):
    name = CharField()
    base_dir = CharField()

    added_at = DateTimeField(default=datetime.datetime.now())


class Directory(BaseModel):
    directory = CharField()
    collection = ForeignKeyField(Collection)

    added_at = DateTimeField(default=datetime.datetime.now())

    def get_filepath(self, filename):
        return '%s/%s'.format(self.directory, filename)


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
        return '%s/%s'.format(dirname, self.filename)


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

	#newFilename, fileExtension = os.path.splitext(filename)[1][1:].strip()
	#print os.path.splitext(filename)[1][1:].strip()
	extension = os.path.splitext(filename)[1][1:].strip().lower()
	#print '[Info] {0} - {1}'.format(filename, fileExtension)

	new_filename = filename.replace(directory,'')
	return (new_filename, extension)


def save_image_info(directory, filename):
    #dirname = get
    print os.stat(filename)
    imageFileinfo = os.stat(filename)

    image = PILImage.open(filename)
    #print image.size

    (purefilename, file_ext) = get_filename(directory.directory, filename)

    #with database.transaction():
    new_image = Image.create(
        directory=directory,
        filename=purefilename,
        file_ext=file_ext,
        added_at=datetime.datetime.now()
    )

    #imageInfo = {'size': imageSize, 'width': image.size[0], 'height': image.size[1]}
    #return imageInfo

    new_image.width = image.size[0]
    new_image.height = image.size[1]
    new_image.filesize = os.stat(filename).st_size

    file = open(filename, 'r')
    parser = PILImageFile.Parser()

    new_image.save()

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


def add_image(conn, imageInfo):
	"""Add a new image tuple to the list"""
	#conn.execute("INSERT INTO image values('{0}', '{1}', '{2}', strftime('now'), strftime('{3}'), '{4}');".format(thisFile, thisDir, thisFileExt, 'now', ''))
	return 42


def update_image(conn, imageInfo):
	"""Updates existing image tuple in the list"""
	return 42


def new_archive(collection, images_dir, archive_dir):
	""" Creates a new image archive in archive_dir
	"""
	print 'Writing new archive to {0}'.format(archive_dir)
	prt('d', 'images_dir: {0}'.format(images_dir,''))

	create_archive()

	imageCounter = 0
	for dirname, dirnames, filenames in os.walk(images_dir):
		thisDir = os.path.join(dirname, '')	# be sure to have trailing / and such
		thisDir = thisDir.replace(images_dir, '')
        directory = Directory.create(directory=thisDir, collection=collection)
		for subdirname in dirnames:
			prt('d', 'dir: {0}'.format(os.path.join(dirname, subdirname)))
		#if thisDir.trim() != '':
		#	conn.execute("INSERT INTO directory values('{0}', strftime('now'), '');".format(thisDir))
		for filename in filenames:
			#print os.path.join(dirname, filename)
			thisFile, thisFileExt = get_filename(images_dir, os.path.join(dirname, filename))
			thisFile = thisFile.replace(thisDir, '')
			#print '[Debug] ext: {0}'.format(thisFileExt)
			if  thisFileExt in IMAGEEXTENSIONS:
				imageInfo = getImageInfo(os.path.join(dirname, filename))
				imageInfo['filename'] = thisFile
				imageInfo['directory'] = thisDir
				imageInfo['extension'] = thisFileExt
				print imageInfo
				addImage(conn, imageInfo)
				conn.execute("INSERT INTO image values('{0}', '{1}', '{2}', strftime('now'), strftime('{3}'), '{4}');".format(thisFile, thisDir, thisFileExt, 'now', ''))
				imageCounter = imageCounter + 1
			else:
				prt('i', 'skipped {0}'.format(filename))

	prt('i', 'added {0} images to archive'.format(imageCounter))

	return 42


def update_archive(images_dir, archive_dir):
	""" Updates existing image archive archive_dir with new images in images_dir"""
	print 'Updating archive {0}'.format(archive_dir)

	# check for DB version, update if necessary

	return 42

