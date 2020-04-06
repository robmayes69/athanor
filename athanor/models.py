from django.db import models
from evennia.typeclasses.models import SharedMemoryModel


class ObjectNamespaceName(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False, unique=True)


class ObjectNamespace(SharedMemoryModel):
    db_object = models.OneToOneField('objects.ObjectDB', related_name='namespace', on_delete=models.CASCADE)
    db_namespace = models.ForeignKey(ObjectNamespaceName, related_name='users', null=True, on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)

    def set_namespace(self, value):
        if value is None:
            self.db_namespace = None
        else:
            namespace, created = ObjectNamespaceName.objects.get_or_create(db_name=value)
            if created:
                namespace.save()
            self.db_namespace = namespace


    class Meta:
        verbose_name = 'Namespace'
        verbose_name_plural = 'Namespaces'
        unique_together = (('db_namespace', 'db_object'), ('db_namespace', 'db_iname'))


class CharacterBridge(SharedMemoryModel):
    """
    A Django Model for storing data particular to Player Characters. Mostly a unique namespace enforce.
    It also tracks which Account a character belongs to.
    """
    db_object = models.OneToOneField('objects.ObjectDB', related_name='character_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_account = models.ForeignKey('accounts.AccountDB', related_name='owned_characters', on_delete=models.SET_NULL,
                                   null=True)

    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'
        unique_together = (('db_namespace', 'db_iname'),)
