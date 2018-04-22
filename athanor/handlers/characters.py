from __future__ import unicode_literals
import datetime, time
from evennia.utils import time_format
from athanor.utils.text import mxp
from athanor.utils.time import utcnow
from athanor.handlers.base import CharacterHandler

from athanor.settings.character import CHARACTER_SYSTEM_SETTINGS


class CharacterSystemHandler(CharacterHandler):
    key = 'athanor_system'
    category = 'athanor_system'
    style = 'fallback'
    system_name = 'SYSTEM'
    settings_classes = CHARACTER_SYSTEM_SETTINGS
    use_hooks = True
    cmdsets = ('athanor.cmdsets.characters.AthCoreCharacterCmdSet', )

    def at_post_puppet(self, **kwargs):
        timestamp = time.time()
        self.owner.attributes.add(key='athanor_system_conn', value=timestamp, category=self.category)

    def is_builder(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Builder)")

    def is_admin(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Admin)")

    def is_developer(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Developer)")

    def status_name(self):
        if self.is_developer():
            return 'Developer'
        if self.is_admin():
            return 'Admin'
        if self.is_builder():
            return 'Builder'
        return 'Mortal'

    def update_account(self, account):
        self.owner.attributes.add(key='account', value=account, category='athanor_settings')
        self.reset_puppet_locks(account)

    @property
    def account(self):
        return self.owner.attributes.get(key='account', category='athanor_settings')

    def update_last_played(self):
        self.owner.attributes.add(key='lastplayed', value=int(utcnow().strftime('%s')), category=self.category)

    @property
    def last_played(self):
        if not self.owner.attributes.has(key='lastplayed', category=self.category):
            self.owner.attributes.add(key='lastplayed', value=int(utcnow().strftime('%s')), category=self.category)
        save_data = self.owner.attributes.get(key='lastplayed', category=self.category)
        return datetime.datetime.utcfromtimestamp(save_data)

    @property
    def connection_time(self):
        timestamp = self.owner.attributes.get(key='athanor_system_conn', category=self.category)
        return time.time() - timestamp

    @property
    def idle_time(self):
        sessions = self.owner.sessions.get()
        if sessions:
            return time.time() - min([ses.cmd_last for ses in sessions])
        return 0

    def off_or_idle_time(self, viewer):
        idle = self.idle_time
        if idle is None or not viewer.ath['athanor_system'].can_see(self.owner):
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self, viewer):
        conn = self.connection_time
        if conn is None or not viewer.ath['athanor_system'].can_see(self.owner):
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.idle_time
        last = self.last_played
        if not idle or not viewer.ath['athanor_system'].can_see(self.owner):
            return viewer.ath['athanor_system'].display_time(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.connection_time
        last = self.last_played
        if not conn or not viewer.ath['athanor_system'].can_see(self.owner):
            return viewer.ath['athanor_system'].display_time(date=last, format='%b %d')
        return time_format(conn, style=1)

    def display_time(self, date=None, format=None):
        return self.account.system.display_time(date, format)

    def load(self):
        if self.owner.attributes.has(key='playtime', category=self.category):
            self.playtime = self.owner.attributes.get(key='playtime', category=self.category)
            return
        self.owner.attributes.add(key='playtime', value=0, category=self.category)
        self.playtime = self.owner.attributes.get(key='playtime', category=self.category)


        return

    def update_playtime(self, seconds):
        self.playtime += seconds

    @property
    def dark(self):
        """
        Dark characters appear offline except to admin.
        """
        return self['dark']

    @property
    def hidden(self):
        """
        Hidden characters only appear on the who list to admin.
        """
        return self['hidden']

    def can_see(self, target):
        if self.is_admin():
            return True
        return not (target.system.idark or target.system.hidden)

    def reset_puppet_locks(self, account):
        """
        Called by the processes for binding a character to a player.
        """
        self.owner.locks.add("puppet:id(%i) or pid(%i) or perm(Developer) or pperm(Admin)" % (self.owner.id, account.id))

    def mxp_name(self, commands=None):
        if not commands:
            commands = ['+finger']
        send_commands = '|'.join(['%s %s' % (command, self.owner.key) for command in commands])
        return mxp(text=self.owner.key, command=send_commands)


class CharacterMode(object):

    def __init__(self, owner):
        self.cmdset = None
        self.owner = owner
        self.mode_dict = dict()
        self.target_dict = dict()

    def get(self, key, default):
        if key in self.mode_dict:
            return self.mode_dict[key]
        self.mode_dict[key] = dict(default)
        return self.mode_dict[key]

    def target(self, key, value=None):
        if key in self.target_dict and not value:
            return self.target_dict[key]
        if value:
            self.target_dict[key] = value
            return value

    def leave(self):
        if not self.cmdset:
            return
        self.owner.cmdset.delete(self.cmdset)
        self.cmdset = None

    def switch(self, cmdset):
        self.leave()
        self.cmdset = cmdset
        self.owner.cmdset.add(cmdset)






class CharacterWhoHandler(CharacterHandler):
    key = 'athanor_who'
    category = 'athanor_who'
    use_hooks = True
    cmdsets = ('athanor.cmdsets.characters.WhoCharacterCmdSet', )

    



ALL = [CharacterSystemHandler, CharacterWhoHandler, ]