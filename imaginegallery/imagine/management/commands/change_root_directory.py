from django.core.management.base import BaseCommand
from imagine.actions import change_root_directory

class Command(BaseCommand):
    help = 'Update the listing and variants of images from all collections, purging non-existing ones'

    def add_arguments(self, parser):
        parser.add_argument('old_dir')
        parser.add_argument('new_dir')

    def handle(self, *args, **options):
        change_root_directory(options['old_dir'], options['new_dir'])
        self.stdout.write(self.style.SUCCESS('Successfully changed paths'))
