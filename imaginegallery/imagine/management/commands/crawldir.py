from django.core.management.base import BaseCommand, CommandError
from imagine.models import Directory

class Command(BaseCommand):
    help = 'Update the listing of images from a certain directory'

    def add_arguments(self, parser):
        parser.add_argument('dir_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for poll_id in options['dir_id']:
            try:
                directory = Directory.objects.get(pk=dir_id)
            except Directory.DoesNotExist:
                raise CommandError('Directory "%s" does not exist' % dir_id)

            print(directory.path)

            self.stdout.write(self.style.SUCCESS('Successfully printed directory "%s"' % dir_id))

