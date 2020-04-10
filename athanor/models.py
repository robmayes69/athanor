from django.db import models
from evennia.typeclasses.models import SharedMemoryModel

from evennia.utils.dbserialize import to_pickle, from_pickle
from evennia.utils.picklefield import PickledObjectField


class HasNames(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        abstract = True


class AbstractNamespace(HasNames):
    db_namespace = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        abstract = True


class AbstractRelations(SharedMemoryModel):
    db_kind = models.CharField(max_length=255, null=False, blank=False)
    db_value = PickledObjectField(null=True)

    # value property (wraps db_value)
    # @property
    def __value_get(self):
        """
        Getter. Allows for `value = self.value`.
        We cannot cache here since it makes certain cases (such
        as storing a dbobj which is then deleted elsewhere) out-of-sync.
        The overhead of unpickling seems hard to avoid.
        """
        return from_pickle(self.db_value, db_obj=self)

    # @value.setter
    def __value_set(self, new_value):
        """
        Setter. Allows for self.value = value. We cannot cache here,
        see self.__value_get.
        """
        self.db_value = to_pickle(new_value)
        # print("value_set, self.db_value:", repr(self.db_value))  # DEBUG
        self.save(update_fields=["db_value"])

    # @value.deleter
    def __value_del(self):
        """Deleter. Allows for del attr.value. This removes the entire attribute."""
        self.delete()

    value = property(__value_get, __value_set, __value_del)

    class Meta:
        unique_together = (('db_from_obj', 'db_to_obj', 'db_kind'),)


class ScriptRelations(AbstractRelations):
    db_from_obj = models.ForeignKey('scripts.ScriptDB', related_name="relations_to", on_delete=models.CASCADE)
    db_to_obj = models.ForeignKey('scripts.ScriptDB', related_name='relations_from', on_delete=models.CASCADE)


class ObjectRelations(AbstractRelations):
    db_from_obj = models.ForeignKey('objects.ObjectDB', related_name="relations_to", on_delete=models.CASCADE)
    db_to_obj = models.ForeignKey('objects.ObjectDB', related_name='relations_from', on_delete=models.CASCADE)


class ScriptNamespace(AbstractNamespace):
    db_script = models.ForeignKey('scripts.ScriptDB', related_name='namespaces', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'ScriptNamespace'
        verbose_name_plural = 'ScriptNamespaces'
        unique_together = (('db_namespace', 'db_script'), ('db_namespace', 'db_iname'))


class ObjectNamespace(AbstractNamespace):
    db_object = models.ForeignKey('objects.ObjectDB', related_name='namespaces', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'ObjectNamespace'
        verbose_name_plural = 'ObjectNamespace'
        unique_together = (('db_namespace', 'db_object'), ('db_namespace', 'db_iname'))


class CharacterBridge(SharedMemoryModel):
    """
    A Django Model for storing data particular to Player Characters. Mostly a unique namespace enforce.
    It also tracks which Account a character belongs to.
    """
    db_script = models.OneToOneField('scripts.ScriptDB', related_name='character_bridge', primary_key=True,
                                     on_delete=models.CASCADE)
    db_account = models.ForeignKey('accounts.AccountDB', related_name='owned_characters', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'PlayerCharacter'
        verbose_name_plural = 'PlayerCharacters'
