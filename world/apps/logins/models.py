from django.db import models
from commands.library import utcnow

# Create your models here.
class Login(models.Model):
    db_player = models.ForeignKey('players.PlayerDB',related_name='logins')
    db_date = models.DateTimeField(default=utcnow())
    db_ip = models.GenericIPAddressField()
    db_site = models.CharField(max_length=300)
    db_result = models.CharField(max_length=200)