import os
from django.db import models
from django.utils.translation import ugettext as _

#from django_extensions.db.fields import AutoSlugField


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
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

    FEATURED_FIRST = 'first'
    FEATURED_LATEST = 'latest'
    FEATURED_OPTIONS = (
        (FEATURED_FIRST, 'First image in (sub)album'),
        (FEATURED_LATEST, 'Newest image in collection'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    base_dir = models.CharField(max_length=255, unique=True)
    archive_dir = models.CharField(max_length=255, blank=True)
    base_uri = models.CharField(max_length=255, blank=True, help_text='Base URI of original images')
    archive_uri = models.CharField(max_length=255, blank=True, help_text='Base URI of image archive')

    # Flat or nested into directories
    flat = models.BooleanField(default=False, help_text='Flatten a collection, or keep the nesting in directories')

    sortmethod = models.CharField(max_length=10, choices=SORT_OPTIONS, default=SORT_DATE_DESC)
    featured_default = models.CharField(max_length=10, choices=FEATURED_OPTIONS, default=FEATURED_LATEST)

    description = models.TextField(null=True, blank=True)

    is_public = models.BooleanField(default=False, help_text='If public, the collection is visible for the world')
    needs_authentication = models.BooleanField(default=False, help_text='User needs to be logged in to view the images')

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

    def get_featured_image(self):
        directories = Directory.objects.filter(collection=self).order_by('relative_path')
        if directories:
            return directories[0].get_featured_image()
        else:
            return None

    def __unicode__(self):
        return '{0} ({1})'.format(self.title, self.base_dir)


class Directory(BaseModel):
    """Directory/collection umbrella object"""
    directory = models.CharField(max_length=255)
    relative_path = models.CharField(max_length=255, help_text='Path relative to Collection base dir')
    collection = models.ForeignKey(Collection)

    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    featured_image = models.ForeignKey('Image', blank=True, null=True, related_name='featured_image')

    parent_directory = models.ForeignKey('self', null=True, blank=True, related_name='children')

    def get_filepath(self, filename):
        return '{0}{1}'.format(self.directory, filename)

    @property
    def dir_name(self):
        if self.title:
            return self.title
        else:
            title = os.path.basename(self.relative_path)
            title = title.replace('_', ' ')
            return title[:1].upper() + title[1:]

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

    def get_featured_image(self):
        if self.featured_image:
            return self.featured_image
        else:
            if self.collection.featured_default == self.collection.FEATURED_FIRST:
                images = self.images(self.collection.sortmethod)
                if images:
                    return images[0]
                else:
                    try:
                        for directory in Directory.objects.filter(parent_directory=self).order_by('relative_path'):
                            images = directory.images(self.collection.sortmethod)
                            if images:
                                return images[0]
                    except Directory.DoesNotExist:
                        # This directory is empty...
                        # TODO: have a fallback thumbnail or something
                        return None
                    return None
            else:
                # Get latest image of this dir and all subdirs
                relative_path = self.relative_path
                if not relative_path:
                    relative_path = '/'
                try:
                    image = Image.objects.filter(collection=self.collection, file_path__icontains=relative_path).order_by('-filter_modified')[0]
                    return image
                except Image.DoesNotExist:
                    return None

    def __unicode__(self):
        return self.directory


class Image(BaseModel):
    """Image object, with generic image file information"""

    IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'cr2']
    IMAGE_EXTENSIONS_RAW = ['cr2']

    collection = models.ForeignKey(Collection)
    directory = models.ForeignKey(Directory, related_name='parent', on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_ext = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)  # Directory path, for quick lookup
    filetype = models.CharField(max_length=255, null=True, blank=True)
    filesize = models.IntegerField(default=-1)

    # Datetime stamps
    file_modified = models.DateTimeField(null=True, blank=True)
    exif_modified = models.DateTimeField(null=True, blank=True)
    # Contains either file_modified or exif_modified, used for filtering into events and such:
    filter_modified = models.DateTimeField(null=True)

    is_visible = models.BooleanField(default=True, help_text='Hide from listing if disable')

    is_photosphere = models.BooleanField(default=False, help_text='Is photo sphere or panorama')

    width = models.IntegerField(default=-1)
    height = models.IntegerField(default=-1)

    image_hash = models.CharField(max_length=255, null=True)
    thumb_hash = models.CharField(max_length=255, null=True, blank=True)

    geo_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geo_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    geo_country = models.CharField(max_length=255, blank=True)  # e.g., 'Netherlands'
    geo_country_code = models.CharField(max_length=5, blank=True)  # e.g., 'NL'
    geo_administrative_area_level_1 = models.CharField(max_length=255, blank=True)  # e.g., 'Noord-Holland'
    geo_administrative_area_level_2 = models.CharField(max_length=255, blank=True)
    geo_city = models.CharField(max_length=255, blank=True)  # e.g., 'Haarlem'
    geo_postal_code = models.CharField(max_length=255, blank=True)
    geo_route = models.CharField(max_length=255, blank=True)  # Street

    geo_formatted_address = models.CharField(max_length=255, blank=True, help_text='Full address from geo API')

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

    def get_exif_highlights(self):
        exif_items = []
        all_exif = ExifItem.objects.filter(image=self)

        exif_tags = [
            'Image Model',
            'EXIF FNumber',
            'EXIF ExposureTime',
            'EXIF Flash',
            'EXIF FocalLength',
            'EXIF ISOSpeedRatings',
            'EXIF LensModel',
            'Image Copyright',
            'Image Artist',
        ]

        for exif in all_exif:
            try:
                if exif.key in exif_tags:
                    exif_items.append({'key': exif.key, 'value': exif.get_value()})
            except KeyError:
                pass

        return exif_items

    def delete_exif_items(self):
        """Delete all exif items belonging to this Image, useful for re-importing afterwards"""
        ExifItem.objects.filter(image__pk=self.pk).delete()

    def get_title(self):
        """Return filename or user-set title from ImageMeta"""
        image_title = self.filename
        try:
            image_meta = ImageMeta.objects.get(image_hash=self.image_hash)
            image_title = image_meta.title
        except ImageMeta.DoesNotExist:
            pass
        return image_title

    def get_variant(self, variant):
        photosize = PhotoSize.objects.get(name=variant)
        if not self.image_hash:
            # Something went wrong with the hashing, no variants available this way
            return None
        return '{}/{}_{}-{}.{}'.format(self.image_hash[:2], self.image_hash, photosize.width, photosize.height, self.file_ext)

    def get_thumbnail(self):
        return self.get_variant('thumbnail')

    def get_normal(self):
        return self.get_variant('normal')

    def get_original(self, collection_basedir):
        return '{}{}/{}'.format(collection_basedir, self.file_path, self.filename)

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
    value_str = models.CharField(max_length=65536, null=True)
    value_int = models.IntegerField(null=True)
    value_float = models.FloatField(null=True)

    def get_value(self):
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


class ImageMeta(BaseModel):
    """
    Metadata for an image, linked by image_hash so it's available for duplicates and
    survives collection rebuilding
    """
    image_hash = models.CharField(max_length=255, primary_key=True)

    title = models.CharField(max_length=255, default='', blank=True)
    description = models.TextField(default='', blank=True)
    #tags


class Comment(BaseModel):
    """Comment on an image"""
    image = models.ForeignKey(ImageMeta)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    comment = models.TextField(default='')


class Stream(BaseModel):
    """Timeframe in which something happened, enabling grouping of images"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(default='')

    start_datetime = models.DateTimeField(null=True, blank=True, help_text='Keep empty to include all history')
    end_datetime = models.DateTimeField(null=True, blank=True, help_text='Keep empty for no enddate')

    sortmethod = models.CharField(max_length=10, choices=Collection.SORT_OPTIONS, default=Collection.SORT_DATE_DESC)

    collections = models.ManyToManyField(Collection, blank=True, help_text='The Collections to include in this stream/event')

    def __unicode__(self):
        return self.title
