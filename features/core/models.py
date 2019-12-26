from django.db import models
from django.core.exceptions import ValidationError
from evennia.utils.ansi import ANSIString
from evennia.abstracts.entity_base import TypedObject
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace


def validate_color(value):
    if not len(ANSIString('|%s' % value)) == 0:
        raise ValidationError("'%s' is not a valid color." % value)


def validate_typeclass(value):
    if not value:
        raise ValidationError("No typeclass path entered!")
    from django.conf import settings
    try:
        typeclass = class_from_module(value, defaultpaths=settings.TYPECLASS_PATHS)
    except Exception:
        raise ValidationError(f"Cannot find Typeclass {value}!")


class TypeclassMap(models.Model):
    db_key = models.CharField(max_length=255, null=False, unique=True, blank=False, validators=[validate_typeclass,])

    def get_typeclass(self):
        try:
            from django.conf import settings
            typeclass = class_from_module(str(self.db_key), defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            return None
        return typeclass


class EntityMapDB(TypedObject):
    __settingclasspath__ = "features.core.core.DefaultEntityMap"
    __defaultclasspath__ = "features.core.core.DefaultEntityMap"
    __applabel__ = "core"

    db_model = models.CharField(max_length=255, null=False, blank=False)
    db_instance = models.IntegerField(null=False)
    db_owner_date_created = models.DateTimeField(null=False)
    db_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('db_model', 'db_instance', 'db_owner_date_created')
        verbose_name = 'EntityMap'
        verbose_name_plural = 'EntityMaps'
