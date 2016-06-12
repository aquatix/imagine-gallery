import datetime

import os
import sys
import click

import imagine
from utilkit import fileutil

#imagine.create_archive()

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

    imagine.DATABASE = os.path.join(archivedir, 'imagine_cli.db')
    imagine.database = imagine.SqliteDatabase(imagine.DATABASE)


if __name__ == '__main__':
    """
    imagine is ran standalone
    """
    cli()
