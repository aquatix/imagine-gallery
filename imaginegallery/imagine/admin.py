from django.contrib import admin
from django.core import urlresolvers
from imagine.models import Collection, Directory, Image, ExifItem, Comment, Event
from imagine.actions import update_collection


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'base_dir', 'archive_dir', 'nr_directories', 'nr_images', )
    search_fields = ('title', 'slug', 'base_dir', 'archive_dir', 'description', )
    prepopulated_fields = {'slug': ('title',), }

    actions = ['refresh']

    def refresh(self, request, queryset):
        for collection in queryset:
            update_collection(collection)
        self.message_user(request, 'Successfully updated {} collection(s)'.format(queryset.count()))


class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('directory', 'nr_images', )


class ImageAdmin(admin.ModelAdmin):
    list_display = ('get_filepath', 'filename', 'width', 'height', 'megapixel', 'filesize', 'image_hash', )
    search_fields = ('filename', )


class ExifItemAdmin(admin.ModelAdmin):
    list_display = ('key', 'get_value', 'from_image', )
    search_fields = ('key', 'value_int', 'value_str', 'value_float', )

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
admin.site.register(ExifItem, ExifItemAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Event, EventAdmin)
