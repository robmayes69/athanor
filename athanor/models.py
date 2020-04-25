from django.db import models
from django.conf import settings

from evennia.typeclasses.models import SharedMemoryModel, TypedObject


class Pluginspace(SharedMemoryModel):
    """
    This model holds database references to all of the Athanor Plugins that have ever been
    installed, in case data must be removed.
    """
    # The name is something like 'athanor' or 'athanor_bbs'. It is an unchanging identifier which
    # uniquely signifies this plugin across all of its versions. It must never change, once established,
    # without a careful migration.
    db_name = models.CharField(max_length=255, null=False, blank=False, unique=True)


class Namespace(SharedMemoryModel):
    db_pluginspace = models.ForeignKey(Pluginspace, related_name='namespaces', on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, null=False, blank=False)

    def __repr__(self):
        return f"<Namespace({self.pk}): {self.db_pluginspace.db_name}-{self.db_name}>"

    def __str__(self):
        return repr(self)

    class Meta:
        unique_together = (('db_pluginspace', 'db_name'),)


class PlayerCharacterDB(TypedObject):
    __settingsclasspath__ = settings.BASE_PLAYER_CHARACTER_TYPECLASS
    __defaultclasspath__ = "athanor.playercharacters.playercharacters.DefaultPlayerCharacter"
    __applabel__ = "athanor"

    # Store the plain text version of a name in db_key

    # Store the version with Evennia-style ANSI markup in here.
    db_ckey = models.CharField(max_length=255, null=False, blank=False)

    db_account = models.ForeignKey('accounts.AccountDB', related_name='player_characters', null=False,
                                   on_delete=models.PROTECT)

    # For games that allow / desire you to list who your alts are, this allows you to show a variety of different
    # Player Characters - each index of (account, alt_number) is an 'alt set' that will be presented to people checking.
    # This allows you to maintain 'hidden alts' on games that allow it.
    db_alt_number = models.PositiveSmallIntegerField(null=True, default=None)

    # This is for total playtime the character has accrued. Accounts also track this for their usage of a character.
    db_total_playtime = models.DurationField(null=False, default=0)

    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )

    # Am inactive character is for soft-deletion / disabling.
    db_is_active = models.BooleanField(null=False, default=True)


class AccountPlayerCombo(SharedMemoryModel):
    """
    This table is used for creating a relationship between specifics accounts and specific Player Characters.
    This is especially useful for games where Player Characters may change hands.
    """
    db_account = models.ForeignKey('accounts.AccountDB', related_name='player_stats', on_delete=models.CASCADE)
    db_player_character = models.ForeignKey(PlayerCharacterDB, related_name='account_stats', on_delete=models.CASCADE)

    # This tracks how much playtime this Account has accrued playing this character.
    db_total_playtime = models.DurationField(null=False, default=0)

    class Meta:
        unique_together = (('db_account', 'db_player_character'),)


class PlaySessionDB(TypedObject):
    __settingsclasspath__ = settings.BASE_PLAY_SESSION_TYPECLASS
    __defaultclasspath__ = "athanor.playsessions.playsessions.DefaultPlaySession"
    __applabel__ = "athanor"

    db_character = models.OneToOneField(PlayerCharacterDB, related_name='play_session', on_delete=models.PROTECT)

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
