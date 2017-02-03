from django.contrib import admin
from django.core import urlresolvers
from imagine.models import Collection, Directory, Image, ImageMeta, PhotoSize, ExifItem, Comment, Event
from imagine.actions import update_collection
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'base_dir', 'archive_dir', 'is_public', 'passwordprotected', 'nr_directories', 'nr_images', )
    search_fields = ('title', 'slug', 'base_dir', 'archive_dir', 'description', )
    prepopulated_fields = {'slug': ('title',), }

    actions = ['refresh']

    def refresh(self, request, queryset):
        for collection in queryset:
            update_collection(collection)
        self.message_user(request, 'Successfully updated {} collection(s)'.format(queryset.count()))


class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('directory', 'relative_path', 'parent_directory', 'collection_link', 'title', 'nr_images', )

    def collection_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:imagine_collection_change", args=(obj.collection.pk,)),
            obj.collection.title
        ))
    collection_link.short_description = 'collection'


class ImageAdmin(admin.ModelAdmin):
    #list_display = ('get_filepath', 'filename', 'width', 'height', 'megapixel', 'filesize', 'image_hash', )
    list_display = ('filename', 'collection_link', 'file_path', 'width', 'height', 'megapixel', 'filter_modified', 'filesize', 'image_hash', 'meta_link', )
    search_fields = ('filename', )
    #readonly_fields = ('imageinegallery_collection_link',)
    list_filter = ('geo_country', 'geo_city', 'is_photosphere', 'is_visible', 'collection', )

    # TODO: use fieldsets to make the form more usable
    # https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets

    def collection_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:imagine_collection_change", args=(obj.directory.collection.pk,)),
            obj.directory.collection.title
        ))
    collection_link.short_description = 'collection'

    def collection_path(self, instance):
        return instance.directory.collection.base_dir

    def meta_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:imagine_imagemeta_change", args=(obj.image_hash,)),
            obj.image_hash
        ))
    meta_link.short_description = 'image meta'


class ImageMetaAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description', 'image_hash', )
    list_display = ('image_hash', 'title', )


class PhotoSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'width', 'height', 'crop_to_fit', )


class ExifItemAdmin(admin.ModelAdmin):
    list_display = ('key', 'get_value', 'from_image', )
    search_fields = ('key', 'value_int', 'value_str', 'value_float', 'image__filename', )

    def from_image(self, obj):
        link=urlresolvers.reverse("admin:imagine_image_change", args=[obj.image.id]) #model name has to be lowercase
        return u'<a href="%s">%s</a>' % (link,obj.image.filename)
    from_image.allow_tags=True


class CommentAdmin(admin.ModelAdmin):
    list_display = ('from_image', 'name', 'email', )
    search_fields = ('name', 'email', 'comment', )

    def from_image(self, obj):
        link=urlresolvers.reverse("admin:imagine_image_change", args=[obj.image.id]) #model name has to be lowercase
        return u'<a href="%s">%s</a>' % (link,obj.image.filename)
    from_image.allow_tags=True


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_datetime', 'end_datetime', )
    search_fields = ('title', 'slug', 'description', )
    prepopulated_fields = {'slug': ('title',), }


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Directory, DirectoryAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(ImageMeta, ImageMetaAdmin)
admin.site.register(PhotoSize, PhotoSizeAdmin)
admin.site.register(ExifItem, ExifItemAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Event, EventAdmin)
