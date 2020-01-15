from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class Host(models.Model):
    address = models.IPAddressField(unique=True, null=False)
    hostname = models.TextField(null=True)
    date_created = models.DateTimeField(null=True)
    date_updated = models.DateTimeField(null=True)


class LoginRecord(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='login_records', on_delete=models.PROTECT)
    host = models.ForeignKey(Host, related_name='logins', on_delete=models.PROTECT)
    date_created = models.DateTimeField(null=False)
    result = models.PositiveSmallIntegerField(default=0)


class CharacterBridge(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='character_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_account = models.ForeignKey('accounts.AccountDB', related_name='owned_characters', on_delete=models.SET_NULL,
                                   null=True)
    db_namespace = models.IntegerField(default=0, null=True)

    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'
        unique_together = (('db_namespace', 'db_iname'),)


class StructureBridge(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='structure_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_structure_path = models.CharField(max_length=255, null=False, blank=False)
    db_system_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)


class RegionBridge(models.Model):
    object = models.OneToOneField('objects.ObjectDB', related_name='region_bridge', primary_key=True,
                                  on_delete=models.CASCADE)
    system_key = models.CharField(max_length=255, blank=False, null=False, unique=True)


class MapBridge(models.Model):
    object = models.OneToOneField('objects.ObjectDB', related_name='map_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    plugin = models.CharField(max_length=255, null=False, blank=False)
    map_key = models.CharField(max_length=255, null=False, blank=False)


class GameLocations(models.Model):
    object = models.ForeignKey('objects.ObjectDB', related_name='saved_locations', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False)
    map = models.ForeignKey('objects.ObjectDB', related_name='objects_here', on_delete=models.CASCADE)
    room_key = models.CharField(max_length=255, null=False, blank=False)
    x_coordinate = models.FloatField(null=True)
    y_coordinate = models.FloatField(null=True)
    z_coordinate = models.FloatField(null=True)

    class Meta:
        unique_together = (('object', 'name'),)


