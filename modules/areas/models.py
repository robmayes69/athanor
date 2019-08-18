from django.db import models
from evennia.typeclasses.models import TypedObject


class AreaDB(TypedObject):
    __settingclasspath__ = "modules.areas.areas.DefaultArea"
    __defaultclasspath__ = "modules.areas.areas.DefaultArea"
    __applabel__ = "areas"

    db_parent = models.ForeignKey('self', null=True, on_delete=models.DO_NOTHING, related_name='children')

    db_fixtures = models.ManyToManyField('objects.ObjectDB', related_name='areas')

    db_transient = models.ManyToManyField('objects.ObjectDB', related_name='current_areas')

    class Meta:
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'
