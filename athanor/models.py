from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from evennia.typeclasses.models import SharedMemoryModel, TypedObject

from evennia.utils.dbserialize import to_pickle, from_pickle
from evennia.utils.picklefield import PickledObjectField


class Pluginspace(SharedMemoryModel):
    """
    This model holds database references to all of the Athanor Plugins that have ever been
    installed, in case data must be removed.
    """
    # The name is something like 'athanor' or 'athanor_bbs'. It is an unchanging identifier which
    # uniquely signifies this plugin across all of its versions. It must never change, once established,
    # without a careful migration.
    db_name = models.CharField(max_length=255, null=False, blank=False, unique=True)


class HasNames(SharedMemoryModel):
    """
    Does a thing have a name? Does it need to be colored? Would it be great if
    that it was perhaps case-insensitively indexed? This is a good start towards
    that.
    """
    # Store the plain text version of a name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    # Store lowercase here. SQLite3 can't case-insensitively collate without
    # hoop-jumping so we do this instead.
    db_iname = models.CharField(max_length=255, null=False, blank=False)

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
        abstract = True
        unique_together = (('db_from_obj', 'db_to_obj', 'db_kind'),)


class ScriptRelations(AbstractRelations):
    db_from_obj = models.ForeignKey('scripts.ScriptDB', related_name="relations_to", on_delete=models.CASCADE)
    db_to_obj = models.ForeignKey('scripts.ScriptDB', related_name='relations_from', on_delete=models.CASCADE)


class ObjectRelations(AbstractRelations):
    db_from_obj = models.ForeignKey('objects.ObjectDB', related_name="relations_to", on_delete=models.CASCADE)
    db_to_obj = models.ForeignKey('objects.ObjectDB', related_name='relations_from', on_delete=models.CASCADE)


class Namespace(SharedMemoryModel):
    db_pluginspace = models.ForeignKey(Pluginspace, related_name='namespaces', on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, null=False, blank=False)

    def __repr__(self):
        return f"<Namespace({self.pk}): {self.db_pluginspace.db_name}-{self.db_name}>"

    def __str__(self):
        return repr(self)

    class Meta:
        unique_together = (('db_pluginspace', 'db_name'),)


class ScriptNamespace(HasNames):
    db_namespace = models.ForeignKey(Namespace, related_name='script_names', on_delete=models.PROTECT)
    db_script = models.ForeignKey('scripts.ScriptDB', related_name='namespaces', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'ScriptNamespace'
        verbose_name_plural = 'ScriptNamespaces'
        unique_together = (('db_namespace', 'db_script'), ('db_namespace', 'db_iname'))


class ObjectNamespace(HasNames):
    db_namespace = models.ForeignKey(Namespace, related_name='object_names', on_delete=models.PROTECT)
    db_object = models.ForeignKey('objects.ObjectDB', related_name='namespaces', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'ObjectNamespace'
        verbose_name_plural = 'ObjectNamespace'
        unique_together = (('db_namespace', 'db_object'), ('db_namespace', 'db_iname'))


class PlayerCharacterDB(TypedObject):
    __settingsclasspath__ = settings.BASE_PLAYER_CHARACTER_TYPECLASS
    __defaultclasspath__ = "athanor.playercharacters.playercharacters.DefaultPlayerCharacter"
    __applabel__ = "athanor"

    # Store the plain text version of a name in db_key

    # Store the version with Evennia-style ANSI markup in here.
    db_ckey = models.CharField(max_length=255, null=False, blank=False)
    # Store lowercase here. SQLite3 can't case-insensitively collate without
    # hoop-jumping so we do this instead.
    db_ikey = models.CharField(max_length=255, null=False, blank=False, unique=True)

    db_account = models.ForeignKey('accounts.AccountDB', related_name='player_characters', null=False,
                                   on_delete=models.PROTECT)

    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )


class PlaySessionDB(TypedObject):
    __settingsclasspath__ = settings.BASE_PLAY_SESSION_TYPECLASS
    __defaultclasspath__ = "athanor.playsessions.playsessions.DefaultPlaySession"
    __applabel__ = "athanor"

    id = models.OneToOneField(PlayerCharacterDB, related_name='play_session', on_delete=models.PROTECT,
                              primary_key=True)


    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )


class HostAddress(models.Model):
    host_ip = models.GenericIPAddressField(null=False)
    host_name = models.TextField(null=True)


class ProtocolName(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)


class ServerSessionDB(TypedObject):
    __settingsclasspath__ = settings.BASE_SERVER_SESSION_TYPECLASS
    __defaultclasspath__ = "athanor.serversessions.serversessions.DefaultServerSession"
    __applabel__ = "athanor"

    id = models.UUIDField(primary_key=True, auto_created=False)
    db_host = models.ForeignKey(HostAddress, null=False, on_delete=models.PROTECT, related_name='sessions')
    db_protocol = models.ForeignKey(ProtocolName, null=False, on_delete=models.PROTECT, related_name='sessions')

    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )

    db_account = models.ForeignKey('accounts.AccountDB', related_name='server_sessions', null=True,
                                   on_delete=models.SET_NULL)

    db_play_session = models.ForeignKey(PlaySessionDB, related_name='server_sessions', null=True,
                                        on_delete=models.SET_NULL)


class EntityDB(TypedObject):
    __settingsclasspath__ = settings.BASE_ENTITY_TYPECLASS
    __defaultclasspath__ = "athanor.entities.entities.DefaultEntity"
    __applabel__ = "athanor"

    # db_key is used as a multi-word collection of words this entity will respond to
    # for commands like 'get' or 'look.' such as 'female goblin'. It is not necessarily
    # the Entity's name.

    # Store the plain text version of a name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    # Store lowercase here. SQLite3 can't case-insensitively collate without
    # hoop-jumping so we do this instead.
    db_iname = models.CharField(max_length=255, null=False, blank=False)

    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )
