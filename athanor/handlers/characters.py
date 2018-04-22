from __future__ import unicode_literals
import datetime, time
from django.conf import settings
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
        self.owner.attributes.add(key='account', value=account, category=self.category)
        self.reset_puppet_locks(account)

    @property
    def account(self):
        return self.owner.attributes.get(key='account', category=self.category)

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
        self.playtime = self.owner.attributes.get(key='playtime', category=self.category)
        if not self.playtime:
            self.owner.attributes.add(key='playtime', value=0, category=self.category)
            self.playtime = self.owner.attributes.get(key='playtime', category=self.category)

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

    def set_banned(self, banned):
        """
        Controls whether this character is banned.
        By this point all input validation should be done.

        :param banned: Integer. Set 0 to disable ban. Set to a UTC TIMESTAMP in seconds to enable.
        :return:
        """
        if not banned:
            self.owner.attributes.remove(key='banned', category=self.category)
            return
        self.owner.attributes.add(key='banned', value=banned, category=self.category)
        until = datetime.datetime.utcfromtimestamp(banned)
        self.disconnect(reason="Character was banned until %s!" % self.display_time(until))

    def set_disabled(self, disabled):
        """
        Controls whether this character is disabled.
        By this point all input validation should be done.

        :param disabled: Boolean. 1 = Disabled. 0 = Re-enable.
        :return:
        """
        if not disabled:
            self.owner.attributes.remove(key='disabled', category=self.category)
            return
        self.owner.attributes.add(key='disabled', value=disabled, category=self.category)
        self.disconnect(reason="Character was disabled!")

    def set_shelved(self, shelved):
        """
        Controls whether this character is shelved.
        By this point all input validation should be done.

        Use shelving and not deleting!

        :param shelved: Boolean. 1 to shelve, 0 to un-shelve.
        :return:
        """
        if not shelved:
            self.owner.swap_typeclass(settings.BASE_CHARACTER_TYPECLASS)
            return
        self.owner.swap_typeclass(settings.ATHANOR_SHELVED_CHARACTER_TYPECLASS)
        self.disconnect(reason="Character was Shelved!")

    def disconnect(self, reason=None):
        """
        Disconnects all sessions from this character.

        :param reason: A string explaining the reason. This will be displayed to the character.
        :return:
        """
        if hasattr(self.owner, 'account'):
            self.console_msg("%s is being disconnected because: %s" % (self.owner, reason))
            for session in self.owner.sessions.get():
                self.owner.account.unpuppet_object(session)


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