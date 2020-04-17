import time

from django.conf import settings

from evennia.objects.objects import DefaultObject, DefaultCharacter, DefaultExit, DefaultRoom

from evennia.utils.utils import lazy_property

import athanor

from athanor.utils.link import PuppetSessionHandler
from athanor.commands.cmdhandler import PuppetCmdHandler
from athanor.commands.cmdsethandler import PuppetCmdSetHandler
from athanor.utils.appearance import PuppetAppearanceHandler


class _AthanorBaseObject:
    """
    General mixin applied to all types of things.

    Events Triggered:
        object_puppet (session): Fired whenever a Connection puppets this object.
        object_disconnect (session): Triggered whenever a Connection disconnects from this account.
        object_online (session): Fired whenever an account comes online from being completely offline.
        object_offline (session): Triggered when an account's final session closes.
    """
    _cmd_sort = 50
    dbtype = 'ObjectDB'
    _cmdset_types = ['object']
    hook_prefixes = ['object']

    @lazy_property
    def sessions(self):
        return PuppetSessionHandler(self)

    @lazy_property
    def cmd(self):
        return PuppetCmdHandler(self)

    @lazy_property
    def cmdset(self):
        return PuppetCmdSetHandler(self)

    def at_cmdset_get(self, **kwargs):
        """
        Load Athanor CmdSets from settings.CMDSETs. Since an object miiiiight be more than one thing....
        """
        if self.ndb._cmdsets_loaded:
            return
        for cmdset_type in self._cmdset_types:
            for cmdset in settings.CMDSETS.get(cmdset_type):
                if not self.cmdset.has(cmdset):
                    self.cmdset.add(cmdset)
        self.ndb._cmdsets_loaded = True

    @property
    def styler(self):
        if (account := self.get_account()):
            return account.styler
        return athanor.STYLER(self)

    @property
    def colorizer(self):
        if (account := self.get_account()):
            return account.colorizer
        return dict()

    def generate_substitutions(self, viewer):
        return {
            "name": self.get_display_name(viewer),
        }

    def system_msg(self, text=None, system_name=None):
        if (account := self.get_account()):
            sysmsg_border = account.options.sys_msg_border
            sysmsg_text = account.options.sys_msg_text
        else:
            sysmsg_border = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_border')[2]
            sysmsg_text = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_text')[2]
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def receive_template_message(self, text, msgobj, target):
        self.system_msg(text=text, system_name=msgobj.system_name)

    def get_puppet(self):
        return self

    def get_account(self):
        return getattr(self, 'account', None)

    def get_player_character(self):
        return getattr(self, 'player_character', None)

    @lazy_property
    def appearance(self):
        return PuppetAppearanceHandler(self)

    def return_appearance(self, looker, **kwargs):
        return self.appearance.render(looker, **kwargs)


    @property
    def idle_time(self):
        """
        Returns the idle time of the least idle session in seconds. If
        no sessions are connected it returns nothing.
        """
        idle = [session.cmd_last_visible for session in self.sessions.all()]
        if idle:
            return time.time() - float(max(idle))
        return None

    @property
    def connection_time(self):
        """
        Returns the maximum connection time of all connected sessions
        in seconds. Returns nothing if there are no sessions.
        """
        conn = [session.conn_time for session in self.sessions.all()]
        if conn:
            return time.time() - float(min(conn))
        return None

    def check_lock(self, lock):
        return self.locks.check_lockstring(self, f"dummy:{lock}")

    @property
    def exits(self):
        return self.contents_get(content_type='exit')


class AthanorItem(_AthanorBaseObject, DefaultObject):
    _content_types = ('item',)
    _cmdset_types = ('item',)


class AthanorRoom(_AthanorBaseObject, DefaultRoom):
    _content_types = ('room',)
    _cmdset_types = ('room',)


class AthanorExit(_AthanorBaseObject, DefaultExit):
    _content_types = ('exit',)
    _cmdset_types = ('exit',)


class AthanorMobile(_AthanorBaseObject, DefaultCharacter):
    """
    The concept of a 'character' has been moved to Identities in Athanor. There are no 'character' objects.
    They are installed called Mobiles. This leads to further delineation such as player avatars and NPCs.
    """
    _content_types = ("mobile",)
    _cmdset_types = ['mobile']


class AthanorAvatar(AthanorMobile):
    """
    This is the default typeclass for the avatars of all Player Characters.
    """
    _cmdset_types = ('mobile', 'avatar')


class AthanorNPC(AthanorMobile):
    """
    This is the default typeclass to use for Non-Player Character entities. Enemies, shopkeepers, animals, whatever.
    """
