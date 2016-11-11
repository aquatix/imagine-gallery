from django.core.management.base import BaseCommand, CommandError
from imagine.models import Collection
from imagine.actions import update_scaled_images

class Command(BaseCommand):
    help = 'Generate scaled versions for images from a certain directory (collection)'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+')

    def handle(self, *args, **options):
        for path in options['path']:
            try:
                collection = Collection.objects.get(base_dir=path)
            except Collection.DoesNotExist:
                raise CommandError('Collection with base dir "%s" does not exist' % path)

            update_scaled_images(collection)

            # TODO: log
            self.stdout.write(self.style.SUCCESS('Successfully updated scaled images for collection "%s"' % path))

