from __future__ import unicode_literals
from django.db import models
from commands.library import utcnow

# Create your models here.
class Login(models.Model):
    player = models.ForeignKey('players.PlayerDB',related_name='logins')
    date = models.DateTimeField(default=utcnow())
    ip = models.GenericIPAddressField()
    site = models.CharField(max_length=300)
    result = models.CharField(max_length=200)