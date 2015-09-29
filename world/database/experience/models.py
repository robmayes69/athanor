from django.db import models
from commands.library import utcnow

# Create your models here.
class Exp(models.Model):
    character_obj = models.ForeignKey('objects.ObjectDB', null=True, related_name='exp')
    group = models.ForeignKey('groups.Group', null=True, related_name='exp')
    amount = models.DecimalField(default=0.0)
    reason = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    date_awarded = models.DateTimeField(default=utcnow())