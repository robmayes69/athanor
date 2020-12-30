from django.conf import settings
from django.db import models
from evennia.typeclasses.models import TypedObject, SharedMemoryModel


class ZoneDB(TypedObject):
    __settingsclasspath__ = settings.BASE_ZONE_TYPECLASS
    __defaultclasspath__ = "athanor.zones.zones.DefaultZone"
    __applabel__ = "zones"

    db_owner = models.ForeignKey('identities.IdentityDB', related_name='zones', on_delete=models.PROTECT)
    db_ikey = models.CharField(max_length=255)
    db_ckey = models.CharField(max_length=255)
    db_core = models.OneToOneField('objects.ObjectDB', null=True, on_delete=models.PROTECT, related_name='zone_core')
    db_room_typeclass = models.CharField(max_length=255, null=True)
    db_exit_typeclass = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = (('db_owner', 'db_ikey'),)
        ordering = ['db_owner__db_namespace__db_priority', 'db_owner__dbnamespace__db_name', 'db_owner__db_key',
                    'db_key']

    def __str__(self):
        return self.db_key


class ZoneLink(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='zone', on_delete=models.CASCADE,
                                     primary_key=True)
    db_zone = models.ForeignKey('zones.ZoneDB', related_name='contents', on_delete=models.CASCADE)
