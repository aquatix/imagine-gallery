from django.contrib import admin
from imagine.models import Collection, Directory, Image, ExifItem, Comment, Event
from imagine.actions import update_collection


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'base_dir', 'archive_dir', )
    search_fields = ('title', 'slug', 'base_dir', 'archive_dir', 'description', )

    actions = ['refresh']

    def refresh(self, request, queryset):
        for collection in queryset:
            update_collection(collection)
        self.message_user(request, 'Successfully updated {} collection(s)'.format(queryset.count()))


class DirectoryAdmin(admin.ModelAdmin):
    pass


class ImageAdmin(admin.ModelAdmin):
    list_display = ('get_filepath', 'filename', 'width', 'height', 'megapixel', 'filesize', 'image_hash', )
    search_fields = ('filename', )


class ExifItemAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


class EventAdmin(admin.ModelAdmin):
    pass


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Directory, DirectoryAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(ExifItem, ExifItemAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Event, EventAdmin)
