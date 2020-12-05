from django.conf import settings
from django.db import models

from evennia.typeclasses.models import TypedObject, SharedMemoryModel


class SectorDB(TypedObject):
    __settingsclasspath__ = settings.BASE_SECTOR_TYPECLASS
    __defaultclasspath__ = "athanor.sectors.zones.DefaultSector"
    __applabel__ = "sectors"

    db_owner = models.ForeignKey('identities.IdentityDB', related_name='sectors', on_delete=models.PROTECT)
    db_ikey = models.CharField(max_length=255)
    db_ckey = models.CharField(max_length=255)

    class Meta:
        unique_together = (('db_owner', 'db_ikey'),)


class SectorLink(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='sector', on_delete=models.CASCADE,
                                     primary_key=True)
    db_sector = models.ForeignKey('sectors.SectorDB', related_name='contents', on_delete=models.CASCADE)
    db_x = models.FloatField(default=0.0, null=False)
    db_y = models.FloatField(default=0.0, null=False)
    db_z = models.FloatField(default=0.0, null=False)

    class Meta:
        index_together = (('db_sector', 'db_object'),)
