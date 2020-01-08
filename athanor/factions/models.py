from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class AllianceBridge(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='alliance_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_abbreviation = models.CharField(max_length=20, null=True, blank=False)
    db_iabbreviation = models.CharField(max_length=20, null=True, blank=False, unique=True)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)


class FactionBridge(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='faction_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_alliance = models.ForeignKey(AllianceBridge, related_name='factions', on_delete=models.PROTECT, null=True)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_abbreviation = models.CharField(max_length=20, null=True, blank=False)
    db_iabbreviation = models.CharField(max_length=20, null=True, blank=False, unique=True)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)

    class Meta:
        verbose_name = 'Faction'
        verbose_name_plural = 'Factions'


class DivisionBridge(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='division_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_faction = models.ForeignKey(FactionBridge, related_name='divisions', on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)

    class Meta:
        unique_together = (('db_faction', 'db_iname'),)
        verbose_name = 'Division'
        verbose_name_plural = 'Divisions'