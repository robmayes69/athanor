from django.conf import settings

from evennia.server.serversession import ServerSession
from evennia.utils.utils import class_from_module

import athanor
from athanor.utils.events import EventEmitter
from athanor.gamedb.base import HasRenderExamine
from evennia.commands.cmdhandler import get_and_merge_cmdsets


MIXINS = [class_from_module(mixin) for mixin in settings.GAMEDB_MIXINS["SESSION"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorSession(*MIXINS, HasRenderExamine, ServerSession, EventEmitter):
    examine_hooks = ['session', 'puppet', 'commands', 'tags', 'attributes']
    examine_type = "session"

    def render_examine(self, viewer):
        get_and_merge_cmdsets(
            self, self, self.get_account(), self.get_puppet(), self.examine_type, "examine"
        ).addCallback(self.render_examine_callback, viewer)

    def render_examine_session(self, viewer, cmdset, styling):
        message = list()
        message.append(f"|wAddress|n: |c{self.address}|n")
        message.append(f"|wProtocol|n: {self.protocol_key}")
        message.append(f"|wTypeclass|n: {self.typename} ({self.typeclass_path})")
        return message

    def render_examine_puppet(self, viewer, cmdset, styling):
        return list()

    @property
    def styler(self):
        if self.account:
            return self.account.styler
        return athanor.STYLER(self)

    @property
    def colorizer(self):
        if self.account:
            return self.account.colorizer
        return dict()

    def at_sync(self):
        """
        This one's a little tricky. It will call methods on the Mixins...
        Used as special hooks for very special plugins.

        Returns:
            None
        """
        ServerSession.at_sync(self)
        for mixin in MIXINS:
            if hasattr(mixin, "mixin_at_sync"):
                mixin.mixin_at_sync(self)

    def generate_substitutions(self, viewer):
        return {
            "name": str(self),
            "address": self.address
        }

    def system_msg(self, text=None, system_name=None, enactor=None):
        sysmsg_border = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_border')[2]
        sysmsg_text = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_text')[2]
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def receive_template_message(self, text, msgobj, target):
        self.system_msg(text=text, system_name=msgobj.system_name)

    def __str__(self):
        account = self.get_account()
        puppet = self.get_puppet()
        address = self.address
        return f"{account.username if account else 'None'}:{puppet.key if puppet else 'None'}@{address} via {self.protocol_key}"

    def render_character_menu_line(self, cmd):
        return f"({self.sessid}) {self.protocol_key} from {self.address} via {self.protocol_key}"
