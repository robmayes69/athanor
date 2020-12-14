import time
from django.utils import timezone

from django.conf import settings

from evennia.utils.utils import lazy_property, class_from_module
from evennia.server.serversession import ServerSession as _BaseServerSession

import evennia
from athanor.conn.handlers import ServerSessionCmdHandler, ServerSessionCmdSetHandler

_ObjectDB = None
_AccountDB = None
_IdentityDB = None
_PlaytimeDB = None


class AthanorServerSession(_BaseServerSession):
    # The Session is always the first thing to matter when parsing commands.
    _cmd_sort = -1000

    def __init__(self):
        self.protocol = "testing"
        self.host = "hostname"
        self.puppet = None
        self.playtime = None
        self.account = None
        self.cmdset_storage = [settings.CMDSET_SESSION, settings.CMDSET_SESSION_LOGINSCREEN]
        self.cmdset = ServerSessionCmdSetHandler(self, True)

    @lazy_property
    def cmd(self):
        return ServerSessionCmdHandler(self)

    @lazy_property
    def temp_styler(self):
        return evennia.PLUGIN_MANAGER["athanor"].styler(self)

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
            "address": self.host,
            "protocol": self.protocol
        }

    def system_msg(self, text=None, system_name=None, enactor=None):
        sysmsg_border = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_border')[2]
        sysmsg_text = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_text')[2]
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def receive_template_message(self, text, msgobj, target):
        self.system_msg(text=text, system_name=msgobj.system_name)

    def render_character_menu_line(self, looker, styling):
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
        self.cmdset_storage = [settings.CMDSET_SESSION, settings.CMDSET_SESSION_SELECTSCREEN]

        # Update account's last login time.
        self.account.last_login = timezone.now()
        self.account.save()

        # add the session-level cmdset
        self.cmdset = ServerSessionCmdSetHandler(self, True)

    def at_sync(self):
        global _ObjectDB, _IdentityDB, _AccountDB, _PlaytimeDB
        if not _IdentityDB:
            from athanor.identities.models import IdentityDB as _IdentityDB
        if not _PlaytimeDB:
            from athanor.playtimes.models import PlaytimeDB as _PlaytimeDB

        super(_BaseServerSession, self).at_sync()

        if not self.logged_in:
            # assign the unloggedin-command set.
            self.cmdset_storage = [settings.CMDSET_SESSION, settings.CMDSET_SESSION_LOGINSCREEN]
            self.cmdset.update(init_mode=True)
        else:
            if self.puid:
                self.create_or_join_playtime(_PlaytimeDB.objects.get(id=self.puid).db_identity, quiet=True)
            else:
                self.cmdset_storage = [settings.CMDSET_SESSION, settings.CMDSET_SESSION_SELECTSCREEN]
                self.cmdset.update(init_mode=True)

    def create_or_join_playtime(self, identity, quiet=False):
        """
        Creates a new playtime and links this Session to it, or locates an existing one and links to that instead.

        An Identity can only have one Playtime at a time.

        Args:
            identity (IdentityDB): The Identity to create a playtime for.
                This should be an instance of CharacterIdentity.
        """
        global _IdentityDB, _PlaytimeDB
        if not _IdentityDB:
            from athanor.identities.models import IdentityDB as _IdentityDB
        if not _PlaytimeDB:
            from athanor.playtimes.models import PlaytimeDB as _PlaytimeDB

        if not (playtime := _PlaytimeDB.objects.filter(db_identity=identity).first()):
            playtime_class = class_from_module(settings.BASE_PLAYTIME_TYPECLASS)
            playtime = playtime_class.create(identity, account=self.account)
        self.link_to_playtime(playtime, quiet)

    def link_to_playtime(self, playtime, quiet):
        """
        Does the hard work of actually linking a Session to a playtime.

        Args:
            playtime (PlaytimeDB): The playtime this Session is being linked to.
            quiet (bool): Whether this should cause loud echoes and other messages.
        """
        self.puid = playtime.dbid
        self.puppet = playtime
        self.cmdset_storage = [settings.CMDSET_SESSION, settings.CMDSET_SESSION_ACTIVEPLAY]
        self.cmdset.update(init_mode=True)
        playtime.sessions.add(self)
        playtime.link_count = playtime.link_count + 1
        if playtime.link_count == 1:
            playtime.at_playtime_start(self, quiet)
        playtime.at_session_link(self, quiet)

    def unlink_from_playtime(self, quiet=False, graceful=True):
        """
        Unlinks a Session from its current Playtime.

        Args:
            quiet (bool): Whether to make a lot of echoes and noises from this process.
            graceful (bool): This is true if it's a clean 'logout' process.
        """
        playtime = self.puppet
        self.puppet = None
        self.puid = None
        playtime.sessions.remove(self)
        playtime.at_session_unlink(self, quiet, graceful)
        if not playtime.sessions.all():
            playtime.at_playtime_end(self, quiet, graceful)
