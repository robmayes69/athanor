from __future__ import unicode_literals
import datetime, time, pytz
from django.conf import settings
from evennia.utils import time_format
from athanor.utils.text import mxp
from athanor.utils.time import utcnow
from athanor.handlers.base import CharacterHandler
from athanor.models import CharacterSettings


class CharacterSystemHandler(CharacterHandler):
    key = 'athanor_system'
    category = 'athanor_system'
    style = 'fallback'
    system_name = 'SYSTEM'
    cmdsets = ('athanor.cmdsets.characters.AthCoreCharacterCmdSet', )

    def __init__(self, base):
        super(CharacterSystemHandler, self).__init__(base)
        self.model, created = CharacterSettings.objects.get_or_create(character=self.owner)

    def at_post_puppet(self, **kwargs):
        self.model.last_login = utcnow()
        self.model.save(update_fields=['last_login'])

    def at_true_logout(self, account, session, **kwargs):
        self.model.last_logout = utcnow()
        self.model.save(update_fields=['last_logout'])

    @property
    def last_played(self):
        return max(self.model.last_login, self.model.last_logout)

    def display_time(self, date=None, format=None):
        return self.account.ath['athanor_system'].display_time(date, format)

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

    @property
    def account(self):
        return self.model.account

    @account.setter
    def account(self, value):
        self.model.account = value
        self.model.save(update_fields=['account'])
        self.reset_puppet_locks(value)

    def reset_puppet_locks(self, account=None):
        """
        Called by the processes for binding a character to a player.
        """
        if account:
            self.owner.locks.add("puppet:id(%i) or pid(%i) or pperm(Developer) or pperm(Admin)" % (self.owner.id, account.id))
        else:
            self.owner.locks.add("puppet:pperm(Developer) or pperm(Admin)")

    def mxp_name(self, commands=None):
        if not commands:
            commands = ['+finger']
        send_commands = '|'.join(['%s %s' % (command, self.owner.key) for command in commands])
        return mxp(text=self.owner.key, command=send_commands)

    @property
    def shelved(self):
        return self.model.shelved

    @shelved.setter
    def shelved(self, value):
        self.model.shelved = value
        self.model.save(update_fields=['shelved', ])
        if value:
            self.disconnect(reason="Character was shelved!")

    @property
    def disabled(self):
        return self.model.disabled

    @disabled.setter
    def disabled(self, value):
        self.model.disabled = value
        self.model.save(update_fields=['disabled', ])
        if value:
            self.disconnect(reason="Character was disabled!")

    @property
    def banned(self):
        data = self.model.banned
        if data > utcnow():
            return data
        return False

    @banned.setter
    def banned(self, value):
        if not value:
            self.model.banned = None
        else:
            self.model.banned = value
            self.disconnect(reason="Character was banned!")
        self.model.save(update_fields=['banned', ])

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


class CharacterWhoHandler(CharacterHandler):
    key = 'who'
    category = 'who'
    system_name = 'WHO'

    @property
    def connection_time(self):
        if not self.owner.sessions.count():
            return 0
        count = min([sess.conn_time for sess in self.owner.sessions.get()])
        return time.time() - count

    @property
    def idle_time(self):
        sessions = self.owner.sessions.get()
        if sessions:
            return time.time() - min([ses.cmd_last for ses in sessions])
        return 0

    def off_or_idle_time(self, viewer):
        idle = self.idle_time
        if idle is None or not viewer.ath['system'].can_see(self.owner):
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self, viewer):
        conn = self.connection_time
        if conn is None or not viewer.ath['system'].can_see(self.owner):
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.idle_time
        last = self.last_played
        if not idle or not viewer.ath['system'].can_see(self.owner):
            return viewer.ath['system'].display_time(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.connection_time
        last = self.last_played
        if not conn or not viewer.ath['system'].can_see(self.owner):
            return viewer.ath['system'].display_time(date=last, format='%b %d')
        return time_format(conn, style=1)

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
