from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class CharacterBridge(SharedMemoryModel):
    """
    A Django Model for storing data particular to Player Characters. Mostly a unique namespace enforce.
    It also tracks which Account a character belongs to.
    """
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


class AlternateNamespaceName(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False, unique=True)


class AlternateNamespace(SharedMemoryModel):
    db_object = models.ForeignKey('objects.ObjectDB', related_name='alternate_namespace', on_delete=models.CASCADE)
    db_namespace = models.ForeignKey(AlternateNamespaceName, related_name='users', on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = 'Namespace'
        verbose_name_plural = 'Namespaces'
        unique_together = (('db_namespace', 'db_object'), ('db_namespace', 'db_iname'))
