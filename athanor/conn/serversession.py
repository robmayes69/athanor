import time
from django.utils import timezone

from django.conf import settings

from evennia.utils.utils import lazy_property
from evennia.server.serversession import ServerSession as _BaseServerSession

import evennia
from athanor.conn.handlers import ServerSessionCmdHandler, ServerSessionCmdSetHandler

_ObjectDB = None
_AccountDB = None
_IdentityDB = None


class AthanorServerSession(_BaseServerSession):
    # The Session is always the first thing to matter when parsing commands.
    _cmd_sort = -1000

    def __init__(self):
        self.puppet = None
        self.account = None
        self.cmdset_storage_string = ""
        self.cmdset = ServerSessionCmdSetHandler(self, True)

    @lazy_property
    def cmd(self):
        return ServerSessionCmdHandler(self)

    @lazy_property
    def temp_styler(self):
        return evennia.PLUGINS["athanor"].styler(self)

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

    def at_login(self, account):
        """
        Largely copied from its parent class, but with some edits.
        """
        self.account = account
        self.uid = self.account.id
        self.uname = self.account.username
        self.logged_in = True
        self.conn_time = time.time()
        self.puid = None
        self.puppet = None
        self.cmdset_storage = settings.CMDSET_SESSION

        # Update account's last login time.
        self.account.last_login = timezone.now()
        self.account.save()

        # add the session-level cmdset
        self.cmdset = ServerSessionCmdSetHandler(self, True)

    def at_sync(self):
        global _ObjectDB, _IdentityDB, _AccountDB
        if not _ObjectDB:
            from evennia.objects.models import ObjectDB as _ObjectDB
        if not _IdentityDB:
            from athanor.identities.models import IdentityDB as _IdentityDB

        super().at_sync()
        if not self.logged_in:
            # assign the unloggedin-command set.
            self.cmdset_storage = settings.CMDSET_UNLOGGEDIN

        self.cmdset.update(init_mode=True)

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
