from django.core.management.base import BaseCommand
from imagine.actions import update_everything

class Command(BaseCommand):
    help = 'Update the listing and variants of images from all collections, purging non-existing ones'

    def handle(self, *args, **options):
        update_everything()

        # TODO: log
        self.stdout.write(self.style.SUCCESS('Successfully updated everything'))

