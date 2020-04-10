from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class ObjectNamespace(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='namespace', on_delete=models.CASCADE)
    db_namespace = models.CharField(max_length=255, null=True, blank=False)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = 'Namespace'
        verbose_name_plural = 'Namespaces'
        unique_together = (('db_namespace', 'db_object'), ('db_namespace', 'db_iname'))


class CharacterBridge(SharedMemoryModel):
    """
    A Django Model for storing data particular to Player Characters.
    It also tracks which Account a character belongs to.
    """
    db_object = models.OneToOneField('objects.ObjectDB', related_name='character_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_account = models.ForeignKey('accounts.AccountDB', related_name='owned_characters', on_delete=models.SET_NULL,
                                   null=True)

    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'


class LocationStorage(models.Model):
    obj = models.ForeignKey('objects.ObjectDB', related_name='location_save', on_delete=models.CASCADE)
    location = models.ForeignKey('objects.ObjectDB', related_name='linked_by', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = (('obj', 'name'),)
