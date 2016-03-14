from django.db import models
from commands.library import utcnow

# Create your models here.
class ExpType(models.Model):
    character_obj = models.ForeignKey('objects.ObjectDB', null=True, related_name='exp')
    type_name = models.CharField(max_length=50, db_index=True)
    group = models.ForeignKey('groups.Group', null=True, related_name='exp')

class Exp(models.Model):
    type = models.ForeignKey('experience.ExpType', related_name='entries')
    amount = models.DecimalField(default=0.0, db_index=True)
    reason = models.CharField(max_length=200)
    source = models.ForeignKey('communications.ObjectStub', null=True)
    date_awarded = models.DateTimeField(default=utcnow())
