from django.db import models
from django.core.exceptions import ValidationError
from evennia.utils.ansi import ANSIString
from evennia.typeclasses.models import SharedMemoryModel
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


class TypeclassMap(SharedMemoryModel):
    db_key = models.CharField(max_length=255, null=False, unique=True, blank=False, validators=[validate_typeclass,])

    def get_typeclass(self):
        try:
            from django.conf import settings
            typeclass = class_from_module(str(self.db_key), defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            return None
        return typeclass


class RelationshipDB(SharedMemoryModel):
    db_holder = models.ForeignKey('objects.ObjectDB', related_name='relationships', on_delete=models.CASCADE)
    db_kind = models.CharField(max_length=255, null=False, blank=False)
    db_object = models.ForeignKey('objects.ObjectDB', related_name='links', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('db_holder', 'db_kind', 'db_object'),)


class MastersDB(SharedMemoryModel):
    db_extension = models.CharField(max_length=255, null=False, blank=False)
    db_kind = models.CharField(max_length=255, null=False, blank=False)
    db_key = models.CharField(max_length=255, null=False, blank=False)
    db_used = models.ManyToManyField('objects.ObjectDB', related_name='masters')

    class Meta:
        unique_together = (('db_extension', 'db_kind', 'db_key'),)
