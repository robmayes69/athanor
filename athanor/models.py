from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from evennia.typeclasses.models import SharedMemoryModel, TypedObject


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
    db_pluginspace = models.ForeignKey(Pluginspace, related_name='namespaces', on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, null=False, blank=False)

    def __repr__(self):
        return f"<Namespace({self.pk}): {self.db_pluginspace.db_name}-{self.db_name}>"

    def __str__(self):
        return repr(self)

    class Meta:
        unique_together = (('db_pluginspace', 'db_name'),)


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

    # Store the plain text version of a name in db_key. We might as well use it.

    # Store the version with Evennia-style ANSI markup in here.
    db_ckey = models.CharField(max_length=255, null=False, blank=False)

    db_namespace = models.ForeignKey(Namespace, related_name='identities', on_delete=models.PROTECT)

    # All Identities have an owner. Bereft of any other, Identities default to the Evennia Superuser.
    db_account = models.ForeignKey('accounts.AccountDB', related_name='owned_identities', on_delete=models.SET_DEFAULT,
                                   default=1)

    db_cmdset_storage = models.CharField(
        "cmdset",
        max_length=255,
        null=True,
        blank=True,
        help_text="optional python path to a cmdset class.",
    )

    class Meta:
        ordering = ['-db_namespace__db_pluginspace__db_name', '-db_namespace__db_name', 'db_account__username', 'db_key']


class AccountIdentityCombo(SharedMemoryModel):
    """
    This table is used for creating a relationship between specifics accounts and specific Player Characters.
    This is especially useful for games where Player Characters may change hands.
    """
    db_account = models.ForeignKey('accounts.AccountDB', related_name='player_stats', on_delete=models.CASCADE)
    db_identity = models.ForeignKey(IdentityDB, related_name='account_stats', on_delete=models.CASCADE)

    # This tracks how much playtime this Account has accrued playing this character.
    db_total_playtime = models.DurationField(null=False, default=0)

    # For games that allow / desire you to list who your alts are, this allows you to show a variety of different
    # Player Characters - each index of (account, alt_number) is an 'alt set' that will be presented to people checking.
    # This allows you to maintain 'hidden alts' on games that allow it.
    db_alt_number = models.PositiveSmallIntegerField(null=True, default=None)

    # Am inactive entry is for soft-deletion / disabling. If active is False, this Character will not appear in the
    # account's character select screen.
    db_is_active = models.BooleanField(null=False, default=True)

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
    __defaultclasspath__ = "athanor.bbs_boards.bbs_boards.DefaultBBSBoard"
    __applabel__ = "athanor"

    db_owner = models.ForeignKey(IdentityDB, on_delete=models.CASCADE, related_name='owned_boards')
    db_ikey = models.CharField(max_length=255, blank=False, null=False)
    db_ckey = models.CharField(max_length=255, blank=False, null=False)
    db_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.db_key)

    class Meta:
        verbose_name = 'BBS'
        verbose_name_plural = 'BBSs'
        unique_together = (('db_owner', 'db_order'), ('db_owner', 'db_ikey'))


class BBSPostDB(TypedObject):
    __settingsclasspath__ = settings.BASE_BBS_POST_TYPECLASS
    __defaultclasspath__ = "athanor.bbs_posts.bbs_posts.DefaultBBSPost"
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

    @classmethod
    def validate_key(cls, key_text, rename_from=None):
        return key_text

    @classmethod
    def validate_order(cls, order_text, rename_from=None):
        return int(order_text)

    def __str__(self):
        return self.subject

    def post_alias(self):
        return f"{self.board.alias}/{self.order}"

    def can_edit(self, checker=None):
        if self.owner.account_stub.account == checker:
            return True
        return self.board.check_permission(checker=checker, type="admin")

    def edit_post(self, find=None, replace=None):
        if not find:
            raise ValueError("No text entered to find.")
        if not replace:
            replace = ''
        self.date_modified = utcnow()
        self.text = self.text.replace(find, replace)

    def update_read(self, account):
        acc_read, created = self.read.get_or_create(account=account)
        acc_read.date_read = utcnow()
        acc_read.save()

    def fullname(self):
        return f"BBS Post: ({self.board.db_script.prefix_order}/{self.order}): {self.name}"

    def generate_substitutions(self, viewer):
        return {'name': self.name,
                'cname': self.cname,
                'typename': 'BBS Post',
                'fullname': self.fullname}


class BBSPostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(BBSPostDB, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'post'),)


class ChannelDB(TypedObject):
    __settingsclasspath__ = settings.BASE_CHANNEL_TYPECLASS
    __defaultclasspath__ = "athanor.channels.channels.DefaultChannel"
    __applabel__ = "athanor"

    db_owner = models.ForeignKey(IdentityDB, on_delete=models.CASCADE, related_name='owned_channels')
    db_ckey = models.CharField(max_length=255, blank=False, null=False)


class ChannelSubscription(SharedMemoryModel):
    db_channel = models.ForeignKey(ChannelDB, related_name='subscriptions', on_delete=models.CASCADE)
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
