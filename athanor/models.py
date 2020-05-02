from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from evennia.typeclasses.models import SharedMemoryModel, TypedObject
from athanor.utils.time import utcnow


class Pluginspace(SharedMemoryModel):
    """
    This model holds database references to all of the Athanor Plugins that have ever been
    installed, in case data must be removed.
    """
    # The name is something like 'athanor' or 'mod_name'. It is an unchanging identifier which
    # uniquely signifies this plugin across all of its versions. It must never change, once established,
    # without a careful migration.
    db_name = models.CharField(max_length=255, null=False, blank=False, unique=True)


class Namespace(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False, unique=True)

    def __repr__(self):
        return f"<Namespace({self.pk}): {self.db_name}>"

    def __str__(self):
        return repr(self)


class IdentityDB(TypedObject):
    """
    The IdentityDB is a new Evennia Typeclass which is used for keeping track of Player Characters, Non-Player
    Characters, Nations, Factions, Parties, and any other such 'named things' for which Access Control Lists are
    relevant. In General, Identities should be deleted with care; a Party might only last for a week, a Faction might
    be entirely disbanded, but Player Characters may have BBS posts or other events attached to them which makes
    deletion a bad idea.
    """
    __settingsclasspath__ = settings.BASE_IDENTITY_TYPECLASS
    __defaultclasspath__ = "athanor.identities.identities.DefaultIdentity"
    __applabel__ = "athanor"

    # db_key is treated as case-insensitively unique per namespace. It's used for system purposes such as
    # plugin-defined Identities remaining addressable by fixtures even if their display name changes.

    # db_name is case-insensitively unique per namespace.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_cname = models.CharField(max_length=255, null=False, blank=False)

    db_namespace = models.ForeignKey(Namespace, related_name='identities', on_delete=models.PROTECT)

    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )


class IdentityFixture(SharedMemoryModel):
    db_identity = models.OneToOneField(IdentityDB, related_name='fixture_data', on_delete=models.PROTECT,
                                       primary_key=True)
    db_pluginspace = models.ForeignKey(Pluginspace, related_name='identity_fixtures', on_delete=models.PROTECT)
    db_key = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = (('db_pluginspace', 'db_key'),)


class AccountIdentityCombo(SharedMemoryModel):
    """
    This table is used for creating a relationship between specifics accounts and specific Player Characters.
    This is especially useful for games where Player Characters may change hands.
    """
    db_account = models.ForeignKey('accounts.AccountDB', related_name='identity_stats', on_delete=models.CASCADE)
    db_identity = models.ForeignKey(IdentityDB, related_name='account_stats', on_delete=models.CASCADE)

    # This tracks how much playtime this Account has accrued playing this character.
    # Add all Account-Identity combos together for a Character to get their total playtime ever!
    db_total_playtime = models.DurationField(null=False, default=0)

    # For games that allow / desire you to list who your alts are, this allows you to show a variety of different
    # Player Characters - each index of (account, alt_number) is an 'alt set' that will be presented to people checking.
    # This allows you to maintain 'hidden alts' on games that allow it.
    db_alt_number = models.PositiveSmallIntegerField(null=True, default=None)

    # Am inactive entry is for soft-deletion / disabling. If active is False, this Character will not appear in the
    # account's character select screen.
    db_is_active = models.BooleanField(null=False, default=True)

    # This will mark the first time that an Account 'touches' this Identity.
    db_date_created = models.DateTimeField(null=False, auto_now_add=True)

    class Meta:
        unique_together = (('db_account', 'db_identity'),)


class PlaySessionDB(TypedObject):
    __settingsclasspath__ = settings.BASE_PLAY_SESSION_TYPECLASS
    __defaultclasspath__ = "athanor.playsessions.playsessions.DefaultPlaySession"
    __applabel__ = "athanor"

    db_combo = models.OneToOneField(AccountIdentityCombo, related_name='play_session', on_delete=models.PROTECT)

    # This will store a record of 'when this PlaySession was last known to be active.' It is used only in the event
    # of a crash for playtime calculations during cleanup.
    db_date_good = models.DateTimeField(null=False)

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
    db_cmd_total = models.PositiveIntegerField(default=0, null=True)
    db_is_active = models.BooleanField(default=True, null=False)
    db_cmd_last = models.DateTimeField(null=True)
    db_cmd_last_visible = models.DateTimeField(null=True)


    db_account = models.ForeignKey('accounts.AccountDB', related_name='server_sessions', null=True,
                                   on_delete=models.SET_NULL)

    db_play_session = models.ForeignKey(PlaySessionDB, related_name='server_sessions', null=True,
                                        on_delete=models.SET_NULL)


class ACLPermission(models.Model):
    name = models.CharField(max_length=50, null=False, unique=True, blank=False)


class ACLEntry(models.Model):
    # This Generic Foreign Key is the object being 'accessed'.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
    object_id = models.PositiveIntegerField(null=False)
    resource = GenericForeignKey('content_type', 'object_id')

    identity = models.ForeignKey(IdentityDB, related_name='acl_references', on_delete=models.CASCADE)
    mode = models.CharField(max_length=30, null=False, blank=True, default='')
    deny = models.BooleanField(null=False, default=False)
    permissions = models.ManyToManyField(ACLPermission, related_name='entries')

    class Meta:
        unique_together = (('content_type', 'object_id', 'identity', 'mode', 'deny'),)
        index_together = (('content_type', 'object_id', 'deny'),)


class BBSBoardDB(TypedObject):
    __settingsclasspath__ = settings.BASE_BBS_BOARD_TYPECLASS
    __defaultclasspath__ = "athanor.bbs.boards.DefaultBoard"
    __applabel__ = "athanor"

    db_owner = models.ForeignKey(IdentityDB, on_delete=models.CASCADE, related_name='owned_boards')
    db_ckey = models.CharField(max_length=255, blank=False, null=False)
    db_order = models.PositiveIntegerField(default=0)
    db_next_post_number = models.PositiveIntegerField(default=0, null=False)

    ignoring = models.ManyToManyField(IdentityDB, related_name='ignored_boards')

    def __str__(self):
        return str(self.db_key)

    class Meta:
        verbose_name = 'BBS'
        verbose_name_plural = 'BBSs'
        unique_together = (('db_owner', 'db_order'), )


class BBSPostDB(TypedObject):
    __settingsclasspath__ = settings.BASE_BBS_POST_TYPECLASS
    __defaultclasspath__ = "athanor.bbs.posts.DefaultPost"
    __applabel__ = "athanor"

    db_poster = models.ForeignKey(IdentityDB, related_name='owned_posts', on_delete=models.PROTECT)
    db_ckey = models.CharField(max_length=255, blank=False, null=False)
    db_date_created = models.DateTimeField(null=False)
    db_board = models.ForeignKey(BBSBoardDB, related_name='posts', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(null=False)
    db_order = models.PositiveIntegerField(null=False)
    db_body = models.TextField(null=False, blank=False)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_board', 'db_order'), )


class BBSPostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(BBSPostDB, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'post'),)


class ChannelOwner(SharedMemoryModel):
    db_owner = models.ForeignKey(IdentityDB, on_delete=models.CASCADE, related_name='owned_channels')
    db_channel = models.OneToOneField('comms.ChannelDB', null=False, related_name='owner', on_delete=models.CASCADE)


class ChannelSubscription(SharedMemoryModel):
    db_channel = models.ForeignKey('comms.ChannelDB', related_name='subscriptions', on_delete=models.CASCADE)
    db_subscriber = models.ForeignKey(AccountIdentityCombo, related_name='channel_subs', on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    db_iname = models.CharField(max_length=255, null=False, blank=False)
    db_namespace = models.CharField(max_length=255, null=False, blank=False)
    db_codename = models.CharField(max_length=255, null=True, blank=False)
    db_ccodename = models.CharField(max_length=255, null=True, blank=False)
    db_icodename = models.CharField(max_length=255, null=True, blank=False)
    db_title = models.CharField(max_length=255, null=True, blank=False)
    db_altname = models.CharField(max_length=255, null=True, blank=False)
    db_muted = models.BooleanField(default=False, null=False, blank=False)
    db_enabled = models.BooleanField(default=True, null=False, blank=False)

    class Meta:
        unique_together = (('db_channel', 'db_subscriber'), ('db_subscriber', 'db_iname'),
                           ('db_channel', 'db_icodename'))


class DimensionDB(TypedObject):
    """
    Unlike the others, Dimensions are ALWAYS Fixtures. A Dimension should never be created unless save for
    by the Asset load process.
    """
    __settingsclasspath__ = settings.BASE_DIMENSION_TYPECLASS
    __defaultclasspath__ = "athanor.dimensions.dimensions.DefaultDimension"
    __applabel__ = "athanor"

    # db_key is treated as case-insensitively unique for this table.
    # Store the plain text version of a name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)


class SectorDB(TypedObject):
    __settingsclasspath__ = settings.BASE_SECTOR_TYPECLASS
    __defaultclasspath__ = "athanor.sectors.sectors.DefaultSector"
    __applabel__ = "athanor"

    # db_key is treated as case-insensitively unique per-dimension for this table, per-dimension.
    # Using a pre-fix for runtime-generated Sectors is advisable.

    db_dimension = models.ForeignKey(DimensionDB, related_name='sectors', on_delete=models.PROTECT)
    # Store the plain text version of a name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)

    # Do I want to use a Vector2 or a Vector3 for the coordinates of a Sector in a dimension?
    # I suppose you could always ignore the Z...


class EntityDB(TypedObject):
    """
    This is Athanor's replacement to Evennia's ObjectDB.
    """
    __settingsclasspath__ = settings.BASE_ENTITY_TYPECLASS
    __defaultclasspath__ = "athanor.entities.entities.DefaultEntity"
    __applabel__ = "athanor"

    # db_key must be case-insensitively unique globally. This isn't a name, it's an identifier.
    # Use a pre-fix for runtime-generated stuff.
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
    equipsets = GenericRelation('athanor.EquipDB', related_query_name='entities')


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
    __settingsclasspath__ = settings.BASE_ROOM_TYPECLASS
    __defaultclasspath__ = "athanor.rooms.rooms.DefaultRoom"
    __applabel__ = "athanor"

    # db_key is used as a unique-key for identifying this Room within a particular Entity.
    # db_key is used for database exports and generating structures with consistent results.
    # If new rooms are created in play, be careful to ensure they have a prefix.
    # something like cust_whatever. This will prevent conflicts.
    db_entity = models.ForeignKey(EntityDB, related_name='rooms', on_delete=models.CASCADE)
    # Store the plain text version of the room's display name in this field.
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)
    # all rooms belong to a given Entity. The Entity is the namespace for a Room.

    class Meta:
        unique_together = (('db_entity', 'db_key'),)


class ExitDB(TypedObject):
    __settingsclasspath__ = settings.BASE_EXIT_TYPECLASS
    __defaultclasspath__ = "athanor.exits.exits.DefaultExit"
    __applabel__ = "athanor"

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
    __settingsclasspath__ = settings.BASE_INVENTORY_TYPECLASS
    __defaultclasspath__ = "athanor.inventories.inventories.DefaultInventory"
    __applabel__ = "athanor"

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


class EquipDB(TypedObject):
    """
    Like with Inventories, there may be many kinds of Equip sets. This might be anything from a paper-doll style
    inventory to a spaceship's part slots or maybe slotting gems into an sword to give it magical powers.

    This is powered by GenericForeignKey so that ANYTHING can equip Items.
    """
    __settingsclasspath__ = settings.BASE_EQUIP_TYPECLASS
    __defaultclasspath__ = "athanor.equips.equips.DefaultEquip"
    __applabel__ = "athanor"

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
    db_equip = models.ForeignKey(EquipDB, related_name='equipped_things', on_delete=models.CASCADE)
    db_entity = models.ForeignKey(EntityDB, related_name='equipped_locations', on_delete=models.CASCADE)

    # The slot is the 'name' of the equipment slot this thing exists in. 'head' or 'socket' or 'about' or whatever.
    db_slot = models.CharField(max_length=80, null=False, blank=False)

    # the layer is the number corresponding to the 'layer' of the item. Some old MUDs love their multi-player gear sets
    # This could also be used for something like where in EVE Online you have an entire row of 'high power slots' for
    # your important active lasers and etc.

    db_layer = models.PositiveIntegerField(default=0, null=False, blank=False)

    class Meta:
        unique_together = (('db_equip', 'db_entity'), ('db_equip', 'db_slot', 'db_layer'))
