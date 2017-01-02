from django.core.management.base import BaseCommand, CommandError
from imagine.models import Collection
from imagine.actions import clean_collection

class Command(BaseCommand):
    help = 'Remove non-existing images from a certain directory (collection)'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+')

    def handle(self, *args, **options):
        for path in options['path']:
            try:
                collection = Collection.objects.get(base_dir=path)
            except Collection.DoesNotExist:
                raise CommandError('Collection with base dir "%s" does not exist' % path)

            number_purged = clean_collection(collection)

            # TODO: log
            self.stdout.write(self.style.SUCCESS('Successfully purged %i non-existing images from collection "%s"' % (number_purged, path)))

