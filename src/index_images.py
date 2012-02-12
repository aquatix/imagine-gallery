import argparse
import os
import sqlite3
import sys

imageExtensions = ['jpg', 'png', 'cr2']


def prt(messageType, message):
	if messageType == 'i':
		print '[Info] {0}'.format(message)
	elif messageType == 'e':
		print '[Error] {0}'.format(message)
	elif messageType == 'd':
		print '[Debug] {0}'.format(message)


def createArchiveDB(archiveDBConn):
	archiveDBConn.execute("CREATE TABLE image(path STRING, filetype STRING, addedAt INTEGER, fileDate INTEGER, meta STRING)")

	archiveDBConn.commit()
	return 0


def getImageFile(imagesDir, filename):

	#newFilename, fileExtension = os.path.splitext(filename)[1][1:].strip()
	#print os.path.splitext(filename)[1][1:].strip()
	fileExtension = os.path.splitext(filename)[1][1:].strip().lower()
	#print '[Info] {0} - {1}'.format(filename, fileExtension)

	newFilename = filename.replace(imagesDir,'')
	return (newFilename, fileExtension)



def newArchive(imagesDir, archiveDir):
	""" Creates a new image archive in archiveDir
	"""
	print 'Writing new archive to {0}'.format(archiveDir)

	imagesDir = os.path.join(imagesDir,'')

	conn = sqlite3.connect(archiveDir + '/archiveDB.sqlite')

	createArchiveDB(conn)
	imageCounter = 0

	prt('d', 'imagesDir: {0}'.format(imagesDir,''))
	for dirname, dirnames, filenames in os.walk(imagesDir):
		for subdirname in dirnames:
			prt('d', 'dir: {0}'.format(os.path.join(dirname, subdirname)))
		for filename in filenames:
			#print os.path.join(dirname, filename)
			thisFile, thisFileExt = getImageFile(imagesDir, os.path.join(dirname, filename))
			#print '[Debug] ext: {0}'.format(thisFileExt)
			if  thisFileExt in imageExtensions:
				conn.execute("INSERT INTO image values('{0}', '{1}', strftime('now'), strftime('{2}'), '{3}');".format(thisFile, thisFileExt, 'now', ''))
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
	return 42



parser = argparse.ArgumentParser(description='Image archive')

parser.add_argument('imagesDir', help='directory with your images')
parser.add_argument('archiveDir', help='directory to store the image archive in')

args = parser.parse_args()
#print vars(args)
#argparse.Namespace(origFile='inputFile')

imagesDir = args.imagesDir
archiveDir = args.archiveDir

#origFile = open(args.inputFile, 'r')
#cleanFile = open(args.outputFile, 'w')

if not os.path.isdir(archiveDir):
	sys.exit('[Error] Archive directory ' + args.archiveDir + ' does not exist')

print 'Scanning {0}'.format(args.imagesDir)

if os.path.isfile(args.archiveDir + '/archiveDB.sqlite'):
	updateArchive(args.imagesDir, args.archiveDir)
else:
	newArchive(args.imagesDir, args.archiveDir)
