from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class Faction(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='faction_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_parent = models.ForeignKey('self', related_name='children', on_delete=models.PROTECT, null=True)
    db_tier = models.PositiveIntegerField(default=0, null=False, blank=False)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_abbreviation = models.CharField(max_length=20, null=True, blank=False)
    db_iabbreviation = models.CharField(max_length=20, null=True, blank=False, unique=True)

    class Meta:
        unique_together = (('db_parent', 'db_iname'),)
        verbose_name = 'Faction'
        verbose_name_plural = 'Factions'
