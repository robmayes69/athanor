from django.conf import settings

from evennia.server.serversession import ServerSession
from evennia.utils.utils import lazy_property

import athanor
from athanor.commands.cmdhandler import SessionCmdHandler
from athanor.utils.events import EventEmitter


class AthanorSession(ServerSession, EventEmitter):

    _cmd_sort = -1000

    def __init__(self, handler):
        """
        Receive the handler through dependency injection.

        Args:
            handler:
        """
        ServerSession.__init__(self)
        self.sessionhandler = handler
        self.pcharacter = None
        self.pcid = None
        self.linked = dict()
        self.linked_sort = list()
        self.linked_state = list()
        self._find_map = self._generate_find_map()

    def _generate_find_map(self):
        return {
            'account': self._find_account,
            'puppet': self._find_object
        }

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

    def _find_entity(self, kind, entity):
        if isinstance(entity, int):
            find_method = self._find_map.get(kind)
            entity = find_method(entity)
            if not entity:
                raise ValueError("Cannot link to a non-existent entity!")
        return entity

    def _sort_links(self):
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
                self._sort_links()

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
            self._sort_links()

    def at_disconnect(self, reason=None):
        """
        Hook called by sessionhandler when disconnecting this session.
        """
        # Gonna have to unlink everything... in reverse order. Puppet first, then Account, etc.
        for kind, entity in reversed(self.linked_sort):
            self.unlink(kind, entity, force=True, reason=reason)

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
        return SessionCmdHandler(self)

    def __str__(self):
        """
        String representation of the user session class. We use
        this a lot in the server logs.
        """
        if not self.linked:
            return f"None@{self.sessid}:{self.address}"
        else:
            account = self.get_account()
            base_str = f"{account.username}({account.dbref})@{self.sessid}:{self.address}"
            extra = self.linked_sort[1:]
            if extra:
                base_str += ":" + ":".join([f"{ent[1].key}({ent[1].dbref})" for ent in self.linked_sort[1:]])
            return base_str
