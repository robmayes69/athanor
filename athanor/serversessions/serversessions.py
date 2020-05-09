from django.conf import settings

from evennia.utils.utils import lazy_property
from evennia.server.serversession import ServerSession

import athanor
from athanor.serversessions.handlers import ServerSessionCmdHandler, ServerSessionCmdSetHandler


class AthanorServerSession(ServerSession):
    # The Session is always the first thing to matter when parsing commands.
    _cmd_sort = -1000

    @lazy_property
    def cmd(self):
        return ServerSessionCmdHandler(self)

    @property
    def styler(self):
        if self.account:
            return self.account.styler
        return athanor.api()['styler'](self)

    @property
    def colorizer(self):
        if self.account:
            return self.account.colorizer
        return dict()

    def generate_substitutions(self, viewer):
        return {
            "name": str(self),
            "address": self.db_host
        }

    def system_msg(self, text=None, system_name=None, enactor=None):
        sysmsg_border = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_border')[2]
        sysmsg_text = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_text')[2]
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def receive_template_message(self, text, msgobj, target):
        self.system_msg(text=text, system_name=msgobj.system_name)

    def render_character_menu_line(self, cmd):
        return f"({self.sessid}) {self.protocol} from {self.host} via {self.protocol}"