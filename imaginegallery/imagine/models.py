import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext as _

#from django_extensions.db.fields import AutoSlugField


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Collection(BaseModel):
    """Collection of images in a certain base_dir"""

    SORT_NAME_ASC = 0
    SORT_NAME_DESC = 1
    SORT_DATE_ASC = 2
    SORT_DATE_DESC = 3
    SORT_OPTIONS = (
        (SORT_NAME_ASC, 'Name ascending'),
        (SORT_NAME_DESC, 'Name descending'),
        (SORT_DATE_ASC, 'Date ascending'),
        (SORT_DATE_DESC, 'Date descending'),
    )

    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=True, blank=True)
    base_dir = models.CharField(max_length=255, blank=True)
    archive_dir = models.CharField(max_length=255, blank=True)

    # Flat or nested into directories
    flat = models.BooleanField(default=False, help_text='Flatten a collection, or keep the nesting in directories')

    sortmethod = models.IntegerField(choices=SORT_OPTIONS, default=SORT_DATE_DESC)

    description = models.TextField(null=True, blank=True)

    password = models.CharField(max_length=255, null=True, blank=True)  # TODO: something with encryption, preferably through a function in the model

    def passwordprotected(self):
        return self.password != ''

    def nr_directories(self):
        return Directory.objects.filter(collection__pk=self.pk).count()

    def nr_images(self):
        total = 0
        for directory in Directory.objects.filter(collection__pk=self.pk):
            total += directory.nr_images()
        return total

    def __unicode__(self):
        return '{0} ({1})'.format(self.title, self.base_dir)


class Directory(BaseModel):
    """Directory/collection umbrella object"""
    directory = models.CharField(max_length=255)
    collection = models.ForeignKey(Collection)

    def get_filepath(self, filename):
        return '{0}{1}'.format(self.directory, filename)

    def nr_images(self):
        return Image.objects.filter(directory__pk=self.pk).count()

    def __unicode__(self):
        return self.directory


class Image(BaseModel):
    """Image object, with generic image file information"""

    IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'cr2']
    IMAGE_EXTENSIONS_RAW = ['cr2']

    directory = models.ForeignKey(Directory, related_name='parent', on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_ext = models.CharField(max_length=255)
    filetype = models.CharField(max_length=255, null=True)
    filesize = models.IntegerField(default=-1)

    # Datetime stamps
    file_modified = models.DateTimeField(null=True)
    exif_modified = models.DateTimeField(null=True)
    # Contains either file_modified or exif_modified, used for filtering into events and such:
    filter_modified = models.DateTimeField(null=True)

    title = models.TextField(default='')
    description = models.TextField(default='')
    is_visible = models.BooleanField(default=True)

    width = models.IntegerField(default=-1)
    height = models.IntegerField(default=-1)

    image_hash = models.CharField(max_length=255, null=True)
    thumb_hash = models.CharField(max_length=255, null=True)

    # TODO: GPS geotag
    # http://stackoverflow.com/questions/10799366/geotagging-jpegs-with-pyexiv2
    # https://pypi.python.org/pypi/geopy
    # https://pypi.python.org/pypi/LatLon

    #class Meta:
    #    order_by = ('filename',)


    def get_filepath(self):
        return '{0}{1}'.format(self.directory.directory, self.filename)


    def get_similar(self):
        return Image.objects.filter(Image.image_hash==self.image_hash)


    def megapixel(self):
        return (self.width * self.height) / 1000000.0


    def modified_datetime(self):
        """Returns file_modified or exif_modified, whichever is more accurate, redundant over filter_modified"""
        if self.exif_modified:
            return self.exif_modified
        else:
            return self.file_modified

    def delete_exif_items(self):
        """Delete all exif items belonging to this Image, useful for re-importing afterwards"""
        ExifItem.objects.filter(image__pk=self.pk).delete()

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
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value_str = models.CharField(max_length=255, null=True)
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

    def __unicode__(self):
        return self.key


class Comment(BaseModel):
    """Comment on an image"""
    image = models.ForeignKey(Image)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    comment = models.TextField(default='')


class Event(BaseModel):
    """Timeframe in which something happened, enabling grouping of images"""
    title = models.CharField(max_length=255)
    description = models.TextField(default='')

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
