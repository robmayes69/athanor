from django.db import models
from django.core.exceptions import ValidationError
from evennia.utils.ansi import ANSIString
from evennia.typeclasses.models import TypedObject

def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)


class ModelMap(models.Model):
    db_key = models.CharField(max_length=255, null=False, unique=True)


class TypeclassMap(models.Model):
    db_key = models.CharField(max_length=255, null=False, unique=True, blank=False)


class EntityMapDB(TypedObject):
    __settingclasspath__ = "features.core.core.DefaultEntityMap"
    __defaultclasspath__ = "features.core.core.DefaultEntityMap"
    __applabel__ = "core"

    db_model = models.ForeignKey(ModelMap, related_name='entities', on_delete=models.PROTECT)
    db_instance = models.IntegerField(null=False)

    class Meta:
        unique_together = ('db_model', 'db_instance')
        verbose_name = 'EntityMap'
        verbose_name_plural = 'EntityMaps'
