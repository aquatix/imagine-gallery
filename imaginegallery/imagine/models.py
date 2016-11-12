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

    SORT_NAME_ASC = 'name_asc'
    SORT_NAME_DESC = 'name_desc'
    SORT_DATE_ASC = 'date_asc'
    SORT_DATE_DESC = 'date_desc'
    SORT_OPTIONS = (
        (SORT_NAME_ASC, 'Name ascending'),
        (SORT_NAME_DESC, 'Name descending'),
        (SORT_DATE_ASC, 'Date ascending'),
        (SORT_DATE_DESC, 'Date descending'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    base_dir = models.CharField(max_length=255, blank=True)
    archive_dir = models.CharField(max_length=255, blank=True)

    # Flat or nested into directories
    flat = models.BooleanField(default=False, help_text='Flatten a collection, or keep the nesting in directories')

    sortmethod = models.CharField(max_length=10, choices=SORT_OPTIONS, default=SORT_DATE_DESC)

    description = models.TextField(null=True, blank=True)

    is_public = models.BooleanField(default=False, help_text='If public, the collection is visible for the world')
    password = models.CharField(max_length=255, null=True, blank=True, help_text='Optionally, password protect this collection')  # TODO: something with encryption, preferably through a function in the model

    def passwordprotected(self):
        return self.password != ''
    passwordprotected.boolean = True

    def nr_directories(self):
        return Directory.objects.filter(collection__pk=self.pk).count()

    def nr_images(self):
        total = 0
        for directory in Directory.objects.filter(collection__pk=self.pk):
            total += directory.nr_images()
        return total

    def images(self):
        images = []
        directories = Directory.objects.filter(collection=self)
        for directory in directories:
            images += directory.images(self.sortmethod)
        return images

    def __unicode__(self):
        return '{0} ({1})'.format(self.title, self.base_dir)


class Directory(BaseModel):
    """Directory/collection umbrella object"""
    directory = models.CharField(max_length=255)
    collection = models.ForeignKey(Collection)
    featured_image = models.ForeignKey('Image', null=True, related_name='featured_image')

    def get_filepath(self, filename):
        return '{0}{1}'.format(self.directory, filename)

    def dir_path(self):
        path = self.directory.replace(self.collection.base_dir, '')
        if path[0] == '/':
            path = path[1:]
        return path

    def nr_images(self):
        return Image.objects.filter(directory__pk=self.pk).count()

    def images(self, sortmethod):
        """ Return all images from this dir, sorted as Collection.sortmethod """
        result = Image.objects.filter(directory=self)
        if sortmethod == Collection.SORT_NAME_DESC:
            return result.order_by('-filename')
        elif sortmethod == Collection.SORT_NAME_ASC:
            return result.order_by('filename')
        elif sortmethod == Collection.SORT_DATE_DESC:
            return result.order_by('-filter_modified')
        elif sortmethod == Collection.SORT_DATE_ASC:
            return result.order_by('filter_modified')

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

    def get_variant(self, variant):
        photosize = PhotoSize.objects.get(name=variant)
        return '{}/{}_{}-{}.jpg'.format(self.image_hash[:2], self.image_hash, photosize.height, photosize.width)

    def get_thumbnail(self):
        return self.get_variant('thumbnail')

    def get_normal(self):
        return self.get_variant('normal')

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


class PhotoSize(BaseModel):
    """ Size configuration """
    name = models.CharField(max_length=20)
    width = models.IntegerField(default=640, help_text='0 for keeping aspect ratio')
    height = models.IntegerField(default=480, help_text='0 for keeping aspect ratio')
    crop_to_fit = models.BooleanField(default=False, help_text="Crop image instead of retaining aspect ratio")

    def __unicode__(self):
        return self.name


class Comment(BaseModel):
    """Comment on an image"""
    image = models.ForeignKey(Image)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    comment = models.TextField(default='')


class Event(BaseModel):
    """Timeframe in which something happened, enabling grouping of images"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(default='')

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
