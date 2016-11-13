# encoding: utf-8

from django.db import models
from django.conf import settings

class CollectionManager(models.Manager):

    def public_collections(self):
        return self.exclude(is_public=False)
