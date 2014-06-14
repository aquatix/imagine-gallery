import datetime

import argparse
import os
import sqlite3
import sys
from socket import gethostname
from PIL import Image, ImageFile
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


class Directory(BaseModel):
    directory = CharField()
    added_at = DateTimeField()


class Image(BaseModel):
    filename = CharField()
    directory = ForeignKeyField(Directory, related_name='parent')
    filetype = CharField()
    filesize = IntegerField()
    file_modified = DateTimeField()

    added_at = DateTimeField()
    description = TextField()

    width = IntegerField()
    height = IntegerField()

    image_hash = CharField()
    thumb_hash = CharField()

    class Meta:
        order_by = ('filename',)


    def get_filename(self):
        dirname = Directory.select().where(
                Directory = self.directory
        )
        return '%s/%s'.format(dirname, self.filename)


class ExifItem(BaseModel):
    image = ForeignKeyField(Image)
    key = CharField()
    value = CharField()
    value_int = IntegerField()
    value_float = FloatField()


def create_archive():
    database.connect()
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


def get_image_info(filename):
	print os.stat(filename)
	imageFileinfo = os.stat(filename)

	image = Image.open(filename)
	#print image.size

    new_image = Image.create(
            filename=filename,
    )

	#imageInfo = {'size': imageSize, 'width': image.size[0], 'height': image.size[1]}
	#return imageInfo

    new_image.width = image.size[0]
    new_image.height = image.size[1]
    new_image.filesize = os.stat(filename).st_size

	file = open(filename, 'r')
	parser = ImageFile.Parser()

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


def new_archive(imagesDir, archiveDir):
	""" Creates a new image archive in archiveDir
	"""
	print 'Writing new archive to {0}'.format(archiveDir)
	prt('d', 'imagesDir: {0}'.format(imagesDir,''))

	conn = sqlite3.connect(archiveDir + DBFILE)

	createArchiveDB(conn, imagesDir)

	imageCounter = 0
	for dirname, dirnames, filenames in os.walk(imagesDir):
		thisDir = os.path.join(dirname, '')	# be sure to have trailing / and such
		thisDir = thisDir.replace(imagesDir, '')
		for subdirname in dirnames:
			prt('d', 'dir: {0}'.format(os.path.join(dirname, subdirname)))
		#if thisDir.trim() != '':
		#	conn.execute("INSERT INTO directory values('{0}', strftime('now'), '');".format(thisDir))
		for filename in filenames:
			#print os.path.join(dirname, filename)
			thisFile, thisFileExt = getImageFile(imagesDir, os.path.join(dirname, filename))
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

	conn.commit()
	conn.close()
	return 42


def update_archive(imagesDir, archiveDir):
	""" Updates existing image archive archiveDir with new images in imagesDir"""
	print 'Updating archive {0}'.format(archiveDir)

	# check for DB version, update if necessary

	return 42

