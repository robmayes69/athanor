from django.conf import settings

from evennia.server.serversession import ServerSession
from evennia.utils.utils import lazy_property

import athanor
from athanor.serversessions.handlers import ServerSessionCmdHandler, ServerSessionCmdSetHandler

_AccountDB = None
_ScriptDB = None
_ObjectDB = None


class AthanorSession(ServerSession):
    # The Session is always the first thing to matter when parsing commands.
    _cmd_sort = -1000

    @lazy_property
    def find_map(self):
        return {
            'account': self._find_account,
            'puppet': self._find_object,
            'playsession': self._find_script
        }

    def __init__(self, handler):
        """
        Receive the handler through dependency injection.

        Args:
            handler:
        """
        ServerSession.__init__(self)
        super().__init__()
        self.sessionhandler = handler
        self.linked = dict()
        self.linked_sort = list()
        self.linked_state = list()
        self.cmdset = ServerSessionCmdSetHandler(self, True)

    @lazy_property
    def cmd(self):
        return ServerSessionCmdHandler(self)

    def _find_account(self, acc_id):
        global _AccountDB
        if not _AccountDB:
            from evennia.accounts.models import AccountDB as _AccountDB
        return _AccountDB.objects.get(id=acc_id)

    def _find_object(self, obj_id):
        global _ObjectDB
        if not _ObjectDB:
            from evennia.objects.models import ObjectDB as _ObjectDB
        return _ObjectDB.objects.get(id=obj_id)

    def _find_script(self, scr_id):
        global _ScriptDB
        if not _ScriptDB:
            from evennia.scripts.models import ScriptDB as _ScriptDB
        return _ObjectDB.objects.get(id=scr_id)

    def _find_entity(self, kind, entity):
        if isinstance(entity, int):
            find_method = self.find_map.get(kind)
            entity = find_method(entity)
            if not entity:
                raise ValueError("Cannot link to a non-existent entity!")
        return entity

    def swap_cmdset(self, cmdset_path):
        """
        Simply reloads the cmdset handler given the path. Used because
        ServerSession's a bit weird.
        """
        self.cmdset_storage = cmdset_path
        self.cmdset = ServerSessionCmdSetHandler(self, True)

    def at_sync(self):
        """
        This is called whenever a session has been resynced with the
        portal.  At this point all relevant attributes have already
        been set and self.account been assigned (if applicable).

        Since this is often called after a server restart we need to
        set up the session as it was.

        """
        for link_kind, link_id in self.linked_state:
            try:
                self.link(link_kind, link_id, sync=True)
            except Exception as e:
                print(str(e))
                # what the heck happened?
                continue

        if not self.logged_in:
            self.swap_cmdset(settings.CMDSET_LOGINSCREEN)

        self.sort_links()

    def sort_links(self):
        self.linked_sort = sorted(self.linked.items(), key=lambda o: o[1]._cmd_sort)
        self.linked_state = [(link_type, entity.pk) for link_type, entity in self.linked_sort]

    def link(self, kind, entity, force=False, sync=False, **kwargs):
        """
        Links the session to an entity.
        Args:
            kind (str): The kind of entity. examples are 'account' and 'puppet'
            entity (object or int): The entity to link, or its ID to lookup.
            sync (bool): Whether this is being called by Portal<->Server synchronization after a reload.
                If yes, this will be passed through to linking calls to smoothly rebuild link state.
        Raises:
              ValueError (string): If any checks fail during linking, will be raised as a ValueError.
                If an exception is raised, no link is performed. Nothing changes.
        Returns:
            entity (object): The entity that was linked.
        """
        entity = self._find_entity(kind, entity)
        if entity.sessions.add(self, force=force, sync=sync):
            self.linked[kind] = entity
            if not sync:
                self.sort_links()

    def unlink(self, kind, entity, force=False, reason=None, **kwargs):
        """
        Unlinks an entity from this session.

        Args:
            kind (str): The kind of entity. examples are 'account' and 'puppet'
            entity (object or int): The entity to unlink, or its ID to lookup.
            force (bool): Don't stop for anything. Mainly used for Unexpected Disconnects
            reason (str or None): A reason that might be displayed down the chain.
        """
        entity = self._find_entity(kind, entity)
        if entity.sessions.remove(self, force=force, reason=reason, **kwargs):
            if kind in self.linked:
                del self.linked[kind]
            self.sort_links()

    def at_disconnect(self, reason=None):
        """
        Hook called by connectionhandler when disconnecting this session.
        """
        # Gonna have to unlink everything... in reverse order. Puppet first, then Account, etc.
        for kind, entity in reversed(self.linked_sort):
            self.unlink(kind, entity, force=True, reason=reason)

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
            "address": self.address
        }

    def system_msg(self, text=None, system_name=None, enactor=None):
        sysmsg_border = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_border')[2]
        sysmsg_text = settings.OPTIONS_ACCOUNT_DEFAULT.get('sys_msg_text')[2]
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def receive_template_message(self, text, msgobj, target):
        self.system_msg(text=text, system_name=msgobj.system_name)

    def render_character_menu_line(self, cmd):
        return f"({self.sessid}) {self.protocol_key} from {self.address} via {self.protocol_key}"

    @lazy_property
    def cmd(self):
        return ServerSessionCmdHandler(self)

    def __str__(self):
        """
        String representation of the user session class. We use
        this a lot in the server logs.
        """
        return repr(self)

    def __repr__(self):
        return f"<({self.sessid}) {self.protocol_key.capitalize()}: {self.get_account()}:" \
               f"{self.get_player_character()}@{self.address}>"

    def get_avatar(self):
        return None

    def get_player_character(self):
        return None

    def get_play_session(self):
        return None
