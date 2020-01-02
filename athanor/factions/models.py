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
    granted_privileges = models.ManyToManyField('factions.FactionPrivilege', related_name="+")

    class Meta:
        unique_together = (('db_parent', 'db_iname'),)
        verbose_name = 'Faction'
        verbose_name_plural = 'Factions'


class FactionPrivilege(SharedMemoryModel):
    db_faction = models.ForeignKey(Faction, related_name='privileges', on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False, unique=True)

    class Meta:
        unique_together = (('db_faction', 'db_name'),)

    def __str__(self):
        return str(self.db_name)


class FactionRank(SharedMemoryModel):
    db_faction = models.ForeignKey(Faction, related_name='members', on_delete=models.CASCADE)
    db_rank_number = models.IntegerField(null=False, blank=False)
    db_name = models.CharField(max_length=255, null=True, blank=True)
    privileges = models.ManyToManyField(FactionPrivilege, related_name='ranks')

    class Meta:
        unique_together = (('db_faction', 'db_rank_number'),)


class FactionMember(SharedMemoryModel):
    db_faction = models.ForeignKey(Faction, related_name='members', on_delete=models.CASCADE)
    db_object = models.ForeignKey('objects.ObjectDB', related_name='factions', on_delete=models.CASCADE)
    db_rank = models.ForeignKey(FactionRank, related_name='members', on_delete=models.PROTECT)
    db_title = models.CharField(max_length=255, null=True, blank=False)
    privileges = models.ManyToManyField(FactionPrivilege, related_name='memberships')
