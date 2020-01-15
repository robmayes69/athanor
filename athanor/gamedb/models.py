from django.db import models
from evennia.typeclasses.models import SharedMemoryModel
from athanor.utils.time import utcnow


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


class Mail(SharedMemoryModel):
    db_subject = models.TextField(null=False, blank=False)
    db_body = models.TextField(null=False, blank=False)

    class Meta:
        verbose_name = 'Mail'
        verbose_name_plural = 'Mail'


class MailLink(SharedMemoryModel):
    db_mail = models.ForeignKey('mail.Mail', related_name='mail_links', on_delete=models.CASCADE)
    db_owner = models.ForeignKey('objects.ObjectDB', related_name='mail_links', on_delete=models.CASCADE)
    db_link_type = models.PositiveSmallIntegerField(default=0)
    db_link_active = models.BooleanField(default=True)
    db_date_read = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'MailLink'
        verbose_name_plural = 'MailLinks'
        unique_together = (('db_mail', 'db_owner'),)
        index_together = (('db_owner', 'db_link_active', 'db_link_type'),)


class Note(SharedMemoryModel):
    db_object = models.ForeignKey('objects.ObjectDB', related_name='notes', on_delete=models.CASCADE)
    db_category = models.CharField(max_length=255, null=False, blank=False)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_contents = models.TextField(blank=False, null=False)
    db_date_created = models.DateTimeField(null=False)
    db_date_modified = models.DateTimeField(null=False)
    db_approved_by = models.ForeignKey('objects.ObjectDB', related_name='approved_notes', on_delete=models.PROTECT, null=True)

    class Meta:
        unique_together = (('db_object', 'db_category', 'db_iname'),)
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'





