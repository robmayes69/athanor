from django.db import models

class CharacterWho(models.Model):
    character = models.OneToOneField('objects.ObjectDB', related_name='+')
    hidden = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)