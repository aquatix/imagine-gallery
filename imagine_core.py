import datetime
from peewee import *

DBVERSION = 1
try:
    DATABASE
except NameError:
    DATABASE = 'imagine.db' # default value

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'cr2']
IMAGE_EXTENSIONS_RAW = ['cr2']

try:
    database
except NameError:
    database = SqliteDatabase(DATABASE)


# == imagine models

class BaseModel(Model):
    class Meta:
        database = database


class Collection(BaseModel):
    name = CharField()
    slug = CharField(null=True)
    base_dir = CharField()

    added_at = DateTimeField(default=datetime.datetime.now())

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.base_dir)


class Directory(BaseModel):
    directory = CharField()
    collection = ForeignKeyField(Collection)

    added_at = DateTimeField(default=datetime.datetime.now())

    def get_filepath(self, filename):
        return '{0}{1}'.format(self.directory, filename)

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
    title = TextField(default='')
    description = TextField(default='')
    is_visible = BooleanField(default=True)

    width = IntegerField(default=-1)
    height = IntegerField(default=-1)

    image_hash = CharField(null=True)
    thumb_hash = CharField(null=True)

    class Meta:
        order_by = ('filename',)


    def get_filepath(self):
        return '{0}{1}'.format(self.directory.directory, self.filename)


    def get_similar(self):
        return Image.select().where(Image.image_hash==self.image_hash)


    def __unicode__(self):
        return self.get_filepath()


class ExifItem(BaseModel):
    image = ForeignKeyField(Image)
    key = CharField()
    value_str = CharField(null=True)
    value_int = IntegerField(null=True)
    value_float = FloatField(null=True)

    def get_value(as_type='str'):
        # TODO: be able to return _int or _float
        return value_str


# the user model specifies its fields (or columns) declaratively, like django
class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email = CharField()
    join_date = DateTimeField()

    class Meta:
        order_by = ('username',)


def create_archive():
    database.connect()
    Collection.create_table()
    Directory.create_table()
    Image.create_table()
    ExifItem.create_table()
    User.create_table()


def is_image(filename):
    f = filename.lower()
    for ext in IMAGE_EXTENSIONS:
        if f.endswith(ext):
            return True
    return False


def get_filename(directory, filename):
    """Return (filename, extension) of the file in filename"""

    #newFilename, fileExtension = os.path.splitext(filename)[1][1:].strip()
    #print os.path.splitext(filename)[1][1:].strip()
    extension = os.path.splitext(filename)[1][1:].strip().lower()
    #print '[Info] {0} - {1}'.format(filename, fileExtension)

    new_filename = filename.replace(directory, '')
    return (new_filename, extension)

