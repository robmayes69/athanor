from __future__ import unicode_literals
from django.db import models


class StaffEntry(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')
    order = models.PositiveSmallIntegerField(default=0)
    position = models.CharField(max_length=255, null=True, blank=True)
    duty = models.BooleanField(default=False)

    def __str__(self):
        return self.character.key