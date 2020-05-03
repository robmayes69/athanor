from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
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


class HostAddress(models.Model):
    host_ip = models.GenericIPAddressField(null=False)
    host_name = models.TextField(null=True)

    def __str__(self):
        return str(self.host_ip)


class ProtocolName(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)

    def __str__(self):
        return str(self.name)


class EntityDB(TypedObject):
    """
    This is Athanor's replacement to Evennia's ObjectDB. It is the core of an Entity-Component System-inspired approach.
    """
    __settingsclasspath__ = settings.BASE_ENTITY_TYPECLASS
    __defaultclasspath__ = "athanor.entities.entities.DefaultEntity"
    __applabel__ = "athanor"


class NameComponent(SharedMemoryModel):
    db_entity = models.OneToOneField(EntityDB, related_name='command_component', on_delete=models.CASCADE)
    db_name = models.CharField(max_length=255, null=False, blank=False)
    # Store the version with Evennia-style ANSI markup in here.
    db_cname = models.CharField(max_length=255, null=False, blank=False)


class CommandComponent(SharedMemoryModel):
    """
    Some entities might need to have CmdSets. Some might not. The storage is handled here.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='command_component', on_delete=models.CASCADE,
                                     primary_key=True)

    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )


class FixtureSpace(SharedMemoryModel):
    db_name = models.CharField(max_length=255, null=False, blank=False, unique=True)


class FixtureComponent(SharedMemoryModel):
    """
    Fixtures are Entities which must exist - they are created by the load process, and integrity checked on server
    start. This table is used for indexing and checking for an Entity's existence.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='fixture_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_fixturespace = models.ForeignKey(FixtureSpace, related_name='fixtures', on_delete=models.PROTECT)
    db_key = models.CharField(max_length=255, null=False, blank=False, unique=True)


class InventoryComponent(SharedMemoryModel):
    """
    Component for entities which ARE an Inventory. Inventories have an Owner, which could literally be 'anything.'
    This allows Factions to have Inventories, or Accounts, etc.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='inventory_component', on_delete=models.CASCADE,
                                     primary_key=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
    object_id = models.PositiveIntegerField(null=False)
    db_owner = GenericForeignKey('content_type', 'object_id')
    db_inventory_key = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = (('content_type', 'object_id', 'db_inventory_key'),)


class InventoryLocationComponent(SharedMemoryModel):
    """
    Component for Entities which are IN an Inventory.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='inventory_location_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_inventory = models.ForeignKey(EntityDB, related_name='inventory_contents', on_delete=models.PROTECT)


class EquipComponent(SharedMemoryModel):
    """
    Component for entities which ARE an EquipSet. EquipSets like Inventories have an Owner, which could be 'anything.'
    """
    db_entity = models.OneToOneField(EntityDB, related_name='equip_component', on_delete=models.CASCADE,
                                     primary_key=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
    object_id = models.PositiveIntegerField(null=False)
    db_owner = GenericForeignKey('content_type', 'object_id')
    db_key = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = (('content_type', 'object_id', 'db_key'),)


class EquipLocationComponent(SharedMemoryModel):
    """
    Component for Entities which are equipped by an EquipSet.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='equip_location_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_equip = models.ForeignKey(EntityDB, related_name='equip_contents', on_delete=models.PROTECT)

    # Should probably stick something in here about how the item is equipped. Slot? Layer?


class DimensionComponent(SharedMemoryModel):
    """
    Component for Entities which ARE a Dimension.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='dimension_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_dimension_key = models.CharField(max_length=255, null=False, blank=False, unique=True)


class SectorComponent(SharedMemoryModel):
    """
    Component for Entities which ARE a Sector.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='sector_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_dimension = models.ForeignKey(EntityDB, related_name='contained_sectors', on_delete=models.PROTECT)
    db_sector_key = models.CharField(max_length=255, null=False, blank=False)
    db_x = models.FloatField(default=0.0, null=False, blank=False)
    db_y = models.FloatField(default=0.0, null=False, blank=False)
    db_z = models.FloatField(default=0.0, null=False, blank=False)

    class Meta:
        unique_together = (('db_dimension', 'db_sector_key'),)


class SectorLocationComponent(SharedMemoryModel):
    """
    Component for Entities that are located 'inside' another Entity in a 3-Dimensional Space.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='sector_location_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_sector = models.ForeignKey(EntityDB, related_name='contained_entities', on_delete=models.PROTECT)
    db_x = models.FloatField(default=0.0, null=False, blank=False)
    db_y = models.FloatField(default=0.0, null=False, blank=False)
    db_z = models.FloatField(default=0.0, null=False, blank=False)


class RoomComponent(SharedMemoryModel):
    """
    Component for Entities which ARE a Room.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='room_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_structure = models.ForeignKey(EntityDB, related_name='contained_rooms', on_delete=models.CASCADE)
    # db_room_key ensures that rooms are uniquely indexed within their containing structure.
    db_room_key = models.CharField(max_length=255, null=False, blank=False)
    db_landing_site = models.BooleanField(null=False, default=False)

    class Meta:
        unique_together = (('db_location', 'db_room_key'),)


class RoomLocationComponent(SharedMemoryModel):
    """
    Component that allows an Entity to exist 'inside' a room.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='room_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_location = models.ForeignKey(EntityDB, related_name='room_contents', on_delete=models.CASCADE)


class GatewayComponent(SharedMemoryModel):
    """
    Component for Exits which ARE a Gateway. (This allows multiple Exits to reference the same 'door' for instance.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='room_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_structure = models.ForeignKey(EntityDB, related_name='contained_gateways', on_delete=models.CASCADE)
    db_gateway_key = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = (('db_structure', 'db_gateway_key'),)


class ExitComponent(SharedMemoryModel):
    """
    Component for Entities that ARE an Exit.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='exit_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_room = models.ForeignKey(EntityDB, related_name='room_contents_exits', on_delete=models.CASCADE)
    db_destination = models.ForeignKey(EntityDB, related_name='exit_entrances', on_delete=models.SET_NULL, null=True)
    db_gateway = models.ForeignKey(EntityDB, related_name='exits_linked', on_delete=models.PROTECT, null=True)
    db_exit_key = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = (('db_location', 'db_exit_key'),)


class IdentityComponent(SharedMemoryModel):
    """
    The Identity component establishes a global set of 'namespaces' for Identities that must be uniquely named within
    certain restrictions, and searchable for purposes of Access Control List usage. Examples include Player Characters,
    Factions, Nations, and Non-Player Characters of importance.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='identity_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_namespace = models.ForeignKey(Namespace, related_name='identities', on_delete=models.PROTECT)
    # When an Entity has an IdentityComponent, its NameComponent's db_name is treated as case-insensitively unique
    # per namespace. Be careful.


class PlayerCharacterComponent(SharedMemoryModel):
    """
    This table is used for creating a relationship between specifics accounts and specific Player Characters.
    This is especially useful for games where Player Characters may change hands.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='player_character_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_account = models.ForeignKey('accounts.AccountDB', related_name='player_character_components',
                                   on_delete=models.PROTECT)

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

    # This will mark the first time that an Account 'touches' this Entity.
    db_date_created = models.DateTimeField(null=False, auto_now_add=True)

    class Meta:
        unique_together = (('db_account', 'db_entity'),)


class BoardComponent(TypedObject):
    """
    Component for Entities which ARE a BBS  Board.
    Beware, the NameComponent is considered case-insensitively unique per board Owner.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='board_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_owner = models.ForeignKey(EntityDB, on_delete=models.CASCADE, related_name='owned_boards')
    db_order = models.PositiveIntegerField(default=0)
    db_next_post_number = models.PositiveIntegerField(default=0, null=False)

    ignoring = models.ManyToManyField(EntityDB, related_name='ignored_boards')

    def __str__(self):
        return str(self.db_key)

    class Meta:
        unique_together = (('db_owner', 'db_order'), )


class BBSPost(SharedMemoryModel):
    db_poster = models.ForeignKey(EntityDB, related_name='+', on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, blank=False, null=False)
    db_came = models.CharField(max_length=255, blank=False, null=False)
    db_date_created = models.DateTimeField(null=False)
    db_board = models.ForeignKey(EntityDB, related_name='+', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(null=False)
    db_order = models.PositiveIntegerField(null=False)
    db_body = models.TextField(null=False, blank=False)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_board', 'db_order'), )


class BBSPostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(BBSPost, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'post'),)


class ChannelComponent(SharedMemoryModel):
    """
    Component for Entities which ARE Channels. These are a replacement for Evennia's Channels!
    Beware, the NameComponent is considered case-insensitively unique per Channel Owner.
    """
    db_entity = models.OneToOneField(EntityDB, related_name='channel_component', on_delete=models.CASCADE,
                                     primary_key=True)
    db_owner = models.ForeignKey(EntityDB, on_delete=models.CASCADE, related_name='owned_channels')


class ChannelSubscription(SharedMemoryModel):
    db_channel = models.ForeignKey(EntityDB, related_name='channel_subscribers', on_delete=models.CASCADE)
    db_subscriber = models.ForeignKey(EntityDB, related_name='channel_subscriptions', on_delete=models.CASCADE)
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


class PlaySessionDB(TypedObject):
    __settingsclasspath__ = settings.BASE_PLAY_SESSION_TYPECLASS
    __defaultclasspath__ = "athanor.playsessions.playsessions.DefaultPlaySession"
    __applabel__ = "athanor"

    db_entity = models.OneToOneField(EntityDB, related_name='play_session', on_delete=models.PROTECT)

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

    entity = models.ForeignKey(EntityDB, related_name='acl_references', on_delete=models.CASCADE)
    mode = models.CharField(max_length=30, null=False, blank=True, default='')
    deny = models.BooleanField(null=False, default=False)
    permissions = models.ManyToManyField(ACLPermission, related_name='entries')

    class Meta:
        unique_together = (('content_type', 'object_id', 'identity', 'mode', 'deny'),)
        index_together = (('content_type', 'object_id', 'deny'),)
