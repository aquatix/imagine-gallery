from django.core.management.base import BaseCommand, CommandError
from imagine.models import Directory

class Command(BaseCommand):
    help = 'Update the listing of images from a certain directory'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+')

    def handle(self, *args, **options):
        for path in options['path']:
            try:
                directory = Directory.objects.get(directory=path)
            except Directory.DoesNotExist:
                raise CommandError('Directory "%s" does not exist' % path)

            print(directory.directory)

            self.stdout.write(self.style.SUCCESS('Successfully printed directory "%s"' % path))

