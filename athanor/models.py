from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

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

    character = models.OneToOneField(PlayerCharacterDB, related_name='play_session', on_delete=models.PROTECT,
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

    def __str__(self):
        return str(self.host_ip)


class ProtocolName(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)

    def __str__(self):
        return str(self.name)


class ServerSessionDB(TypedObject):
    __settingsclasspath__ = settings.BASE_SERVER_SESSION_TYPECLASS
    __defaultclasspath__ = "athanor.serversessions.serversessions.DefaultServerSession"
    __applabel__ = "athanor"

    sessid = models.UUIDField(null=False, unique=True)
    django_session_key = models.CharField(max_length=40, null=True, blank=False, db_index=True)
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


class DimensionDB(TypedObject):
    # Store the plain text version of a name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    # Store lowercase here. SQLite3 can't case-insensitively collate without
    # hoop-jumping so we do this instead.
    # Not really sure if I should make this unique or not yet.
    db_iname = models.CharField(max_length=255, null=False, blank=False)

    # Should Dimensions provide CmdSets? My thought is: sure, why not?
    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )


class DimensionFixture(SharedMemoryModel):
    """
    This table is for any Sectors which are considered 'fixtures', defined in external game assets, and must be
    able to be referred to consistently no matter what happens.
    """
    db_dimension = models.OneToOneField(DimensionDB, related_name='fixture_data', primary_key=True,
                                        on_delete=models.PROTECT)
    # Remember this index is case-sensitive.
    db_key = models.CharField(max_length=255, null=False, blank=False, unique=True)


class SectorDB(TypedObject):
    db_dimension = models.ForeignKey(DimensionDB, related_name='sectors', on_delete=models.PROTECT)
    # Store the plain text version of a name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)

    # Do I want to use a Vector2 or a Vector3 for the coordinates of a Sector in a dimension?
    # I suppose you could always ignore the Z...

    # Should Sectors provide CmdSets? My thought is: sure, why not?
    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )

    class Meta:
        unique_together = (('db_dimension', 'db_key'), ('db_dimension', 'db_key'))


class SectorFixture(SharedMemoryModel):
    """
    This table is for any Sectors which are considered 'fixtures', defined in external game assets, and must be
    able to be referred to consistently no matter what happens.
    """
    db_sector = models.OneToOneField(SectorDB, related_name='fixture_data', primary_key=True, on_delete=models.PROTECT)
    # Remember this index is case-sensitive.
    db_key = models.CharField(max_length=255, null=False, blank=False, unique=True)


class EntityDB(TypedObject):
    """
    This is Athanor's replacement to Evennia's ObjectDB.
    """
    __settingsclasspath__ = settings.BASE_ENTITY_TYPECLASS
    __defaultclasspath__ = "athanor.entities.entities.DefaultEntity"
    __applabel__ = "athanor"

    # db_key is used as a multi-word collection of words this entity will respond to
    # for commands like 'get' or 'look.' such as 'female goblin'. It is not necessarily
    # the Entity's proper name or their display name.
    # Store the plain text version of a name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)

    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )

    inventories = GenericRelation('athanor.InventoryDB', related_name='entities')
    equipsets = GenericRelation('athanor.EquippedDB', related_query_name='entities')


class EntityFixture(SharedMemoryModel):
    """
    This table is for any Entities which are considered 'fixtures'. It contains their unique system identifiers.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='fixture_data', primary_key=True, on_delete=models.PROTECT)
    # Remember this index is case-sensitive.
    db_key = models.CharField(max_length=255, null=False, blank=False, unique=True)


class SectorLocation(SharedMemoryModel):
    db_sector = models.ForeignKey(SectorDB, related_name='sector_contents', on_delete=models.PROTECT)
    db_entity = models.ForeignKey(EntityDB, related_name='sector_locations', on_delete=models.CASCADE)

    # need some kind of vector3 here probably. Again, you could ignore the Z if you really want to I guess?
    # Don't prevent two things from being in the same 'coordinates.' Code logic should handle that, not database.

    class Meta:
        # It probably doesn't make sense for the same entity to exist in more than one Sector. However, maybe for
        # SOME things, it might? You would never want it to be in the same place twice, though.
        unique_together = (('db_sector', 'db_entity'),)


class RoomDB(TypedObject):
    # db_key is used as a unique-key for identifying this Room within a particular Entity.
    # db_key is used for database exports and generating structures with consistent results.
    # If new rooms are created in play, be careful to ensure they have a prefix.
    # something like cust_whatever. This will prevent conflicts.

    # Store the plain text version of the room's display name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    # all rooms belong to a given Entity. The Entity is the namespace for a Room.

    class Meta:
        unique_together = (('db_entity', 'db_key'),)


class ExitDB(TypedObject):
    # db_key is used as a unique-key for identifying this Room within a particular Entity.
    # Store the plain text version of the room's display name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    # all rooms belong to a given Entity. The Entity is the namespace for a Room.
    db_room = models.ForeignKey(RoomDB, related_name='exits', on_delete=models.CASCADE)
    db_destination = models.ForeignKey(RoomDB, related_name='entrances', on_delete=models.SET_NULL, null=True)
    db_pair = models.ForeignKey('self', related_name='linked_exits', on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = (('db_room', 'db_key'),)


class RoomLocation(SharedMemoryModel):
    db_room = models.ForeignKey(RoomDB, related_name='room_contents', on_delete=models.PROTECT)
    # Maybe db_entity should be a one-to-one-field?
    db_entity = models.ForeignKey(EntityDB, related_name='room_locations', on_delete=models.CASCADE)

    # Can you be in more than room at once? Um. Hrm. Maybe...
    # Definitely not twice in the same place, though.
    class Meta:
        unique_together = (('db_room', 'db_entity'),)


class InventoryDB(TypedObject):
    """
    There can be many different kinds of inventories - a shopkeeper's personal inventory and stock may be
    different things. A Capital Ship might have a cargo bay and a fuel hangar. Given this, Inventories are
    TypedObjects.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    owner_object = GenericForeignKey('content_type', 'object_id')
    # db_key is used to identify the type of inventory it is specific to its owner. It must be unique per-entity.

    class Meta:
        unique_together = (('content_type', 'object_id', 'db_key'),)


class InventoryLocation(SharedMemoryModel):
    db_inventory = models.ForeignKey(InventoryDB, related_name='inventory_contents', on_delete=models.CASCADE)
    db_entity = models.ForeignKey(EntityDB, related_name='inventory_locations', on_delete=models.CASCADE)

    # Not sure what other kind of information is useful here yet.
    # probably some way to sort the stuff.

    class Meta:
        # If nothing else, the same item cannot be listed in the same inventory more than once.
        unique_together = (('db_inventory', 'db_entity'), )


class EquippedDB(TypedObject):
    """
    Like with Inventories, there may be many kinds of Equip sets. This might be anything from a paper-doll style
    inventory to a spaceship's part slots or maybe slotting gems into an sword to give it magical powers.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    owner_object = GenericForeignKey('content_type', 'object_id')
    # db_key is used to identify the type of EquippedSet it is specific to its owner. It must be unique per-entity.


    # Not sure what else is relevant to an Equipped set yet.

    class Meta:
        unique_together = (('content_type', 'object_id', 'db_key'),)


class EquipLocation(SharedMemoryModel):
    """
    Simple table for holding information on what's equipped where, with database enforcement.
    """
    db_equip = models.ForeignKey(EquippedDB, related_name='equipped_things', on_delete=models.CASCADE)
    db_entity = models.ForeignKey(EntityDB, related_name='equipped_locations', on_delete=models.CASCADE)

    # The slot is the 'name' of the equipment slot this thing exists in. 'head' or 'socket' or 'about' or whatever.
    db_slot = models.CharField(max_length=80, null=False, blank=False)

    # the layer is the number corresponding to the 'layer' of the item. Some old MUDs love their multi-player gear sets
    # This could also be used for something like where in EVE Online you have an entire row of 'high power slots' for
    # your important active lasers and etc.

    db_layer = models.PositiveIntegerField(default=0, null=False, blank=False)

    class Meta:
        unique_together = (('db_equip', 'db_entity'), ('db_equip', 'db_slot', 'db_layer'))
