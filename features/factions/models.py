from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class AllianceDB(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_object = models.OneToOneField('objects.ObjectDB', related_name='alliance_data', on_delete=models.CASCADE)
    db_abbreviation = models.CharField(max_length=20, null=True, blank=False)
    db_iabbreviation = models.CharField(max_length=20, null=True, blank=False, unique=True)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)

    class Meta:
        verbose_name = 'Alliance'
        verbose_name_plural = 'Alliances'


class FactionDB(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False, unique=True)
    db_alliance = models.ForeignKey(AllianceDB, null=True, related_name='factions', on_delete=models.PROTECT)
    db_object = models.OneToOneField('objects.ObjectDB', related_name='faction_data', on_delete=models.CASCADE)
    db_abbreviation = models.CharField(max_length=20, null=True, blank=False)
    db_iabbreviation = models.CharField(max_length=20, null=True, blank=False, unique=True)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)

    class Meta:
        verbose_name = 'Faction'
        verbose_name_plural = 'Factions'
