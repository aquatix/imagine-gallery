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

    db_file = os.path.join(archivedir, 'imagine_cli.db')
    should_create = True
    print db_file
    if os.path.exists(db_file):
        should_create = False

    imagine.database = imagine.SqliteDatabase(db_file)
    imagine.BaseModel.database = imagine.database

    imagine.init_db(db_file)
    if should_create:
        imagine.create_archive()

    imagine.update_collection('test', 'test-slug', inputdir, archivedir)


if __name__ == '__main__':
    """
    imagine is ran standalone
    """
    cli()
