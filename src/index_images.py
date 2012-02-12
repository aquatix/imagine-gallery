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

	# images info table
	archiveDBConn.execute("CREATE TABLE image(path STRING, filetype STRING, addedAt INTEGER, fileDate INTEGER, meta STRING);")

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

	image = Image.open(filename)
	print image.size
	return 0

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



def newArchive(imagesDir, archiveDir):
	""" Creates a new image archive in archiveDir
	"""
	print 'Writing new archive to {0}'.format(archiveDir)
	prt('d', 'imagesDir: {0}'.format(imagesDir,''))

	conn = sqlite3.connect(archiveDir + DBFILE)

	createArchiveDB(conn, imagesDir)

	imageCounter = 0
	for dirname, dirnames, filenames in os.walk(imagesDir):
		for subdirname in dirnames:
			prt('d', 'dir: {0}'.format(os.path.join(dirname, subdirname)))
		for filename in filenames:
			#print os.path.join(dirname, filename)
			thisFile, thisFileExt = getImageFile(imagesDir, os.path.join(dirname, filename))
			#print '[Debug] ext: {0}'.format(thisFileExt)
			if  thisFileExt in IMAGEEXTENSIONS:
				conn.execute("INSERT INTO image values('{0}', '{1}', strftime('now'), strftime('{2}'), '{3}');".format(thisFile, thisFileExt, 'now', ''))
				imageCounter = imageCounter + 1
				getImageInfo(os.path.join(dirname, filename))
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
