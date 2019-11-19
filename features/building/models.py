from django.db import models
from evennia.typeclasses.models import TypedObject


class AreaDB(TypedObject):
    __settingclasspath__ = "features.building.building.DefaultArea"
    __defaultclasspath__ = "features.building.building.DefaultArea"
    __applabel__ = "building"

    db_parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT, related_name='children')
    db_owner = models.ForeignKey('core.EntityMapDB', related_name='territory', null=True, on_delete=models.SET_NULL)
    db_room_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='building',
                                          on_delete=models.PROTECT)
    db_exit_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='exits',
                                          on_delete=models.PROTECT)
    db_fixtures = models.ManyToManyField('objects.ObjectDB', related_name='building')
    db_transient = models.ManyToManyField('objects.ObjectDB', related_name='current_areas')

    class Meta:
        unique_together = (('db_parent', 'db_key'), )
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'
