from django.core.management.base import BaseCommand
from imagine.actions import change_root_directory

class Command(BaseCommand):
    help = 'Update the listing and variants of images from all collections, purging non-existing ones'

    def add_arguments(self, parser):
        parser.add_argument('old_dir', nargs='+')
        parser.add_argument('new_dir', nargs='+')

    def handle(self, *args, **options):
        try:
            change_root_directory(args['old_dir'], args['new_dir'])
            self.stdout.write(self.style.SUCCESS('Successfully changed paths'))
        except:
            self.stdout.write(self.style.ERROR('Failure during changing of paths'))
