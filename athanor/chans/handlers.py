from django.db.models import Q
from django.conf import settings

from evennia.utils.ansi import ANSIString
from evennia.utils.utils import lazy_property, class_from_module

from athanor.utils.cmdset import BaseAthCmdSet
from athanor.utils.text import partial_match
from athanor.chans.models import ChannelSubscription, ChannelAlias
from athanor.utils import error
from athanor.access.acl import ACLHandler


class ClassHolder:

    @lazy_property
    def classes(self):
        return {family: class_from_module(path) for family, path in settings.CHANNEL_COMMAND_CLASSES.items()}


CLASS_HOLDER = ClassHolder()


class ChannelACLHandler(ACLHandler):
    pass


class AbstractChannelHandler:
    family = None

    def __init__(self, owner):
        self.owner = owner
        self._cached = False
        self._cached_cmdset = None
        self.update_cache()

    def system_msg(self, message):
        self.owner.system_msg(message, system_name=f"{self.family} Channels")

    def update_cache(self):
        cmdset = BaseAthCmdSet()
        cmdset.key = "ChannelCmdSet"
        cmdset.priority = 101
        cmdset.duplicates = True
        for subscription in self.subscriptions.all():
            cmd = CLASS_HOLDER.classes[self.family](
                key=subscription.db_name,
                locks="cmd:all();%s" % subscription.db_channel.locks,
                subscription=subscription
            )
            cmdset.add(cmd)
        self._cached_cmdset = cmdset
        self._cached = True

    def cmdset(self):
        if not self._cached:
            self.update_cache()
        return self._cached_cmdset

    @property
    def subscriptions(self):
        return self.owner.channel_subscriptions

    @property
    def aliases(self):
        return self.owner.channel_subaliases

    def add(self, channel, alias):
        if (found := self.subscriptions.filter(db_name=alias).first()):
            raise error.BadNameException(f"That conflicts with an existing alias to {found.db_channel}!")
        self.subscriptions.create(db_channel=channel, db_name=alias)
        self.update_cache()

    def find_alias(self, alias):
        if isinstance(alias, ChannelSubscription):
            return alias
        aliases = self.aliases.filter()
        if not (found := partial_match(alias, aliases)):
            raise error.TargetNotFoundException(f"Channel Alias not found: {alias}!")
        return found

    def leave(self, alias):
        found = self.find_alias(alias)
        channel = found.db_channel
        found.delete()
        if not self.aliases.filter(db_channel=channel).count():
            self.subscriptions.filter(db_channel=channel).delete()
        self.update_cache()

    def codename(self, alias, codename):
        found = self.find_alias(alias)
        if not codename:
            raise error.SyntaxException("Must include a codename!")
        if codename.lower() == 'none':
            found.db_ccodename = None
            found.db_codename = None
            found.db_icodename = None
            found.save_codename()
            self.system_msg("Codename cleared!")
            return
        codename = ANSIString(codename)
        codename_clean = codename.clean()
        if found.siblings.filter(db_icodename=codename_clean.lower()).count():
            raise ValueError("This codename is already in use! No can do.")
        found.db_ccodename = codename
        found.db_codename = codename_clean
        found.db_icodename = codename_clean.lower()
        found.save_codename()
        self.system_msg(f"Codename set to: {codename}")

    def title(self, alias, title):
        found = self.find_alias(alias)
        if not title:
            raise ValueError("Must include a title!")
        if title.lower() == 'none':
            found.db_altname = None
            found.save(update_fields=['db_title'])
            self.system_msg("Title cleared!")
            return
        title = ANSIString(title)
        found.db_title = title
        found.save(update_fields=['db_title'])
        self.system_msg(f"Title set to: {title}")

    def altname(self, alias, altname):
        found = self.find_alias(alias)
        if not altname:
            raise ValueError("Must include an altname!")
        if altname.lower() == 'none':
            found.db_altname = None
            found.save(update_fields=['db_altname'])
            self.system_msg("Codename cleared!")
            return
        altname = ANSIString(altname)
        found.db_altname = altname
        found.save(update_fields=['db_altname'])
        self.system_msg(f"Altname set to: {altname}")

    def check_listen(self, channel):
        all_aliases = self.subscriptions.filter(db_channel=channel)
        listening = True if self.owner in channel.listeners else False
        # If listening and shouldn't be...
        permission = channel.is_position(self.owner, 'listener')
        if listening:
            if not permission or not all_aliases.filter(Q(db_muted=False) | Q(db_enabled=True)).count():
                channel.remove_listener(self.owner)
        else:
            if permission and all_aliases.filter(Q(db_muted=False) | Q(db_enabled=True)).count():
                channel.add_listener(self.owner)

    def mute(self, alias):
        found = self.find_alias(alias)
        if found.muted:
            raise ValueError("Channel is already muted!")
        found.muted = True
        self.check_listen(found.db_channel)
        self.system_msg("Muted the channel!")

    def unmute(self, alias):
        found = self.find_alias(alias)
        if not found.muted:
            raise ValueError("Channel is not muted!")
        found.muted = False
        self.check_listen(found.db_channel)
        self.system_msg("un-Muted the channel!")

    def on(self, alias):
        found = self.find_alias(alias)
        if found.enabled:
            raise ValueError("Channel is already on!")
        found.enabled = True
        self.check_listen(found.db_channel)
        self.system_msg("Turned channel on!")

    def off(self, alias):
        found = self.find_alias(alias)
        if not found.enabled:
            raise ValueError("Channel is not on!")
        found.enabled = False
        self.check_listen(found.db_channel)
        self.system_msg("Turned channel on!")


class AccountChannelHandler(AbstractChannelHandler):
    family = 'account'


class CharacterChannelHandler(AbstractChannelHandler):
    family = 'character'


class GlobalChannelHandler:
    """
    This actually replaces the Evennia CHANNEL_HANDLER_CLASS
    """

    def __init__(self):
        self._cached_channel_cmds = {}
        self._cached_cmdsets = {}
        self._cached_channels = {}

    def add(self, channel):
        pass

    def clear(self):
        pass

    def remove(self, channel):
        pass

    def update(self):
        pass

    def get_cmdset(self, source_object):
        return source_object.channels.cmdset()
