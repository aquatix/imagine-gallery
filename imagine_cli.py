import datetime

import argparse
import os
import sqlite3
import sys
from socket import gethostname

import imagine

DBVERSION = 1
imagine.DATABASE = 'imagine_cli.db'
imagine.database = imagine.SqliteDatabase(imagine.DATABASE)

imagine.create_archive()

#imagine.Database =

DEBUG = True
#DEBUG = False


def prt(messageType, message):
    if DEBUG == False:
        return

    if messageType == 'i':
        print '[Info] {0}'.format(message)
    elif messageType == 'e':
        print '[Error] {0}'.format(message)
    elif messageType == 'd':
        print '[Debug] {0}'.format(message)


def new_archive(imagesDir, archiveDir):
    """ Creates a new image archive in archiveDir
    """
    print 'Writing new archive to {0}'.format(archiveDir)
    prt('d', 'imagesDir: {0}'.format(imagesDir,''))


def update_archive(imagesDir, archiveDir):
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
