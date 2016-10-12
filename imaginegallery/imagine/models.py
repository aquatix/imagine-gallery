import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from django_extensions.db.fields import AutoSlugField


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Collection(BaseModel):
    """Collection of images in a certain base_dir"""
    name = models.CharField()
    slug = models.CharField(null=True)
    base_dir = models.CharField()

    description = models.CharField(null=True)

    password = models.CharField(null=True)  # TODO: something with encryption, preferably through a function in the model

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.base_dir)


class Directory(BaseModel):
    """Directory/collection umbrella object"""
    directory = models.CharField()
    collection = models.ForeignKey(Collection)

    added_at = models.DateTimeField(default=datetime.datetime.now())

    def get_filepath(self, filename):
        return '{0}{1}'.format(self.directory, filename)

    def __unicode__(self):
        return self.directory


class Image(BaseModel):
    """Image object, with generic image file information"""

    IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'cr2']
    IMAGE_EXTENSIONS_RAW = ['cr2']

    directory = models.ForeignKey(Directory, related_name='parent')
    filename = models.CharField()
    file_ext = models.CharField()
    filetype = models.CharField(null=True)
    filesize = models.IntegerField(default=-1)

    # Datetime stamps
    file_modified = models.DateTimeField(null=True)
    exif_modified = models.DateTimeField(null=True)
    # Contains either file_modified or exif_modified, used for filtering into events and such:
    filter_modified = models.DateTimeField(null=True)

    added_at = models.DateTimeField(default=datetime.datetime.now())
    title = models.TextField(default='')
    description = models.TextField(default='')
    is_visible = models.BooleanField(default=True)

    width = models.IntegerField(default=-1)
    height = models.IntegerField(default=-1)

    image_hash = models.CharField(null=True)
    thumb_hash = models.CharField(null=True)

    # TODO: GPS geotag
    # http://stackoverflow.com/questions/10799366/geotagging-jpegs-with-pyexiv2
    # https://pypi.python.org/pypi/geopy
    # https://pypi.python.org/pypi/LatLon

    class Meta:
        order_by = ('filename',)


    def get_filepath(self):
        return '{0}{1}'.format(self.directory.directory, self.filename)


    def get_similar(self):
        return Image.objects.filter(Image.image_hash==self.image_hash)


    def modified_datetime(self):
        """Returns file_modified or exif_modified, whichever is more accurate, redundant over filter_modified"""
        if self.exif_modified:
            return self.exif_modified
        else:
            return self.file_modified


    @classmethod
    def is_image(cls, filename):
        """Is file in `filename` of a supported image type"""
        f = filename.lower()
        for ext in cls.IMAGE_EXTENSIONS:
            if f.endswith(ext):
                return True
        for ext in cls.IMAGE_EXTENSIONS_RAW:
            if f.endswith(ext):
                return True
        return False


    def __unicode__(self):
        return self.get_filepath()


class ExifItem(BaseModel):
    """Piece of exif info of a certain Image"""
    image = models.ForeignKey(Image)
    key = models.CharField()
    value_str = models.CharField(null=True)
    value_int = models.IntegerField(null=True)
    value_float = models.FloatField(null=True)

    def get_value(self, as_type='str'):
        if self.value_str:
            return self.value_str
        elif self.value_int:
            return self.value_int
        elif self.value_float:
            return self.value_float
        else:
            return None


class Comment(BaseModel):
    """Comment on an image"""
    image = models.ForeignKey(Image)
    name = models.CharField()
    email = models.CharField()
    comment = models.CharField()


class Event(BaseModel):
    """Timeframe in which something happened, enabling grouping of images"""
    title = models.CharField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
