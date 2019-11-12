from django.db import models
from evennia.typeclasses.models import TypedObject


class AreaDB(TypedObject):
    __settingclasspath__ = "features.areas.areas.DefaultArea"
    __defaultclasspath__ = "features.areas.areas.DefaultArea"
    __applabel__ = "areas"

    db_parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT, related_name='children')
    db_alliance = models.ForeignKey('factions.AllianceDB', related_name='territory', null=True, on_delete=models.SET_NULL)
    db_faction = models.ForeignKey('factions.FactionDB', related_name='territory', null=True, on_delete=models.SET_NULL)
    db_fixtures = models.ManyToManyField('objects.ObjectDB', related_name='areas')
    db_transient = models.ManyToManyField('objects.ObjectDB', related_name='current_areas')

    class Meta:
        unique_together = (('db_parent', 'db_key'), )
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'
