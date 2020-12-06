from django.conf import settings

from evennia.utils.utils import lazy_property
from evennia.server.serversession import ServerSession

import evennia
from athanor.serversessions.handlers import ServerSessionCmdHandler, ServerSessionCmdSetHandler


class AthanorServerSession(ServerSession):
    # The Session is always the first thing to matter when parsing commands.
    _cmd_sort = -1000

    def __init__(self):
        super(ServerSession, self).__init__()
        self.identity_id = None

    @lazy_property
    def cmd(self):
        return ServerSessionCmdHandler(self)

    @lazy_property
    def temp_styler(self):
        return evennia.PLUGIN_API["athanor"].styler(self)

    @property
    def styler(self):
        if self.account:
            return self.account.styler
        return self.temp_styler

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

    def at_sync(self):
        global _ObjectDB
        if not _ObjectDB:
            from evennia.objects.models import ObjectDB as _ObjectDB

        super(ServerSession, self).at_sync()
        if not self.logged_in:
            # assign the unloggedin-command set.
            self.cmdset_storage = settings.CMDSET_UNLOGGEDIN

        self.cmdset.update(init_mode=True)

        if self.identity_id:
            pass

        if self.puid:
            # reconnect puppet (puid is only set if we are coming
            # back from a server reload). This does all the steps
            # done in the default @ic command but without any
            # hooks, echoes or access checks.
            obj = _ObjectDB.objects.get(id=self.puid)
            obj.sessions.add(self)
            obj.account = self.account
            self.puid = obj.id
            self.puppet = obj
            # obj.scripts.validate()
            obj.locks.cache_lock_bypass(obj)