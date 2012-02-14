import argparse
import os
import sqlite3
import sys
from socket import gethostname
from PIL import Image, ImageFile

DBVERSION = 1
DBFILE = 'imagine.sqlite'
IMAGEEXTENSIONS = ['jpg', 'png', 'cr2']

#DEBUG = True
DEBUG = False


def prt(messageType, message):
	if DEBUG == False:
		return

	if messageType == 'i':
		print '[Info] {0}'.format(message)
	elif messageType == 'e':
		print '[Error] {0}'.format(message)
	elif messageType == 'd':
		print '[Debug] {0}'.format(message)


def createArchiveDB(archiveDBConn, imagesDir):
	# meta table
	archiveDBConn.execute("CREATE TABLE archive(dbVersion INTEGER, host STRING, path STRING, created INTEGER);")
	archiveDBConn.execute("INSERT INTO archive values ({0}, '{1}', '{2}', 'now');".format(DBVERSION, gethostname(), imagesDir))

	# directories info table
	archiveDBConn.execute("CREATE TABLE directory(path STRING, addedAt INTEGER, meta STRING);")

	# images info table
	archiveDBConn.execute("""
		CREATE TABLE image(filename STRING,
		directory STRING,
		filetype STRING,
		addedAt INTEGER,
		fileDate INTEGER, meta STRING);""")

	archiveDBConn.commit()
	return 0


def getImageFile(imagesDir, filename):

	#newFilename, fileExtension = os.path.splitext(filename)[1][1:].strip()
	#print os.path.splitext(filename)[1][1:].strip()
	fileExtension = os.path.splitext(filename)[1][1:].strip().lower()
	#print '[Info] {0} - {1}'.format(filename, fileExtension)

	newFilename = filename.replace(imagesDir,'')
	return (newFilename, fileExtension)


def getImageInfo(filename):
	print os.stat(filename)
	imageFileinfo = os.stat(filename)
	imageSize = os.stat(filename).st_size

	image = Image.open(filename)
	#print image.size

	imageInfo = {'size': imageSize, 'width': image.size[0], 'height': image.size[1]}
	return imageInfo




	file = open(filename, 'r')
	parser = ImageFile.Parser()

	while True:
		s = file.read(1024)
		if not s:
			break
		parser.feed(s)
	image = parser.close()


	print image.size
	#rw, rh = image.size()
	#print image.size

#	print image.fileName()
#	print image.magick()
#	print image.size().width()
#	print image.size().height()


def addImage(conn, imageInfo):
	"""Add a new image tuple to the list"""
	#conn.execute("INSERT INTO image values('{0}', '{1}', '{2}', strftime('now'), strftime('{3}'), '{4}');".format(thisFile, thisDir, thisFileExt, 'now', ''))
	return 42


def updateImage(conn, imageInfo):
	"""Updates existing image tuple in the list"""
	return 42


def newArchive(imagesDir, archiveDir):
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


def updateArchive(imagesDir, archiveDir):
	""" Updates existing image archive archiveDir with new images in imagesDir"""
	print 'Updating archive {0}'.format(archiveDir)

	# check for DB version, update if necessary

	return 42



parser = argparse.ArgumentParser(description='Image archive')

parser.add_argument('imagesDir', help='directory with your images')
parser.add_argument('archiveDir', help='directory to store the image archive in')

args = parser.parse_args()
#print vars(args)
#argparse.Namespace(origFile='inputFile')

imagesDir = args.imagesDir
archiveDir = args.archiveDir

# expand directories and appending / if needed
imagesDir = os.path.join(imagesDir,'')
archiveDir = os.path.join(archiveDir,'')

if not os.path.isdir(archiveDir):
	sys.exit('[Error] Archive directory ' + archiveDir + ' does not exist')

print 'Scanning {0}'.format(imagesDir)

if os.path.isfile(args.archiveDir + '/' + DBFILE):
	updateArchive(imagesDir, archiveDir)
else:
	newArchive(imagesDir, archiveDir)
