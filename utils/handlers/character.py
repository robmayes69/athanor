from __future__ import unicode_literals

from evennia.utils import time_format


class CharacterWeb(object):
    def __init__(self, owner):
        self.owner = owner

    def serialize(self, viewer):
        return {'id': self.owner.id, 'key': self.owner.key, 'conn': self.owner.connection_time,
                'idle': self.owner.idle_time,
                'conn_pretty': self.owner.time.off_or_conn_time(viewer),
                'idle_pretty': self.owner.time.last_or_idle_time(viewer)}

    def login_serialize(self):
        return {'id': self.owner.id, 'key': self.owner.key, 'admin': self.owner.is_admin()}

    def full_update(self):
        self.owner.who.update_character(self.owner)


class CharacterTime(object):
    def __init__(self, owner):
        self.owner = owner
        self.config = owner.config

    def last_played(self, update=False):
        if update:
            self.config.update_last_played()
        return self.config.last_played

    def off_or_idle_time(self, viewer):
        idle = self.owner.idle_time
        if idle is None or not viewer.time.can_see(self.owner):
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self, viewer):
        conn = self.owner.connection_time
        if conn is None or not viewer.time.can_see(self.owner):
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.owner.idle_time
        last = self.config.last_played
        if not idle or not viewer.time.can_see(self.owner):
            return viewer.time.display(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.owner.connection_time
        last = self.config.last_played
        if not conn or not viewer.time.can_see(self.owner):
            return viewer.time.display(date=last, format='%b %d')
        return time_format(conn, style=1)

    def display(self, date=None, format=None):
        return self.owner.owner.time.display(date, format)


    def is_dark(self, value=None):
        """
        Dark characters appear offline except to admin.
        """
        if value is not None:
            self.owner.db._dark = value
            self.owner.sys_msg("You %s DARK." % ('are now' if value else 'are no longer'))
        return self.owner.db._dark

    def is_hidden(self, value=None):
        """
        Hidden characters only appear on the who list to admin.
        """
        if value is not None:
            self.owner.db._hidden = value
            self.owner.sys_msg("You %s HIDDEN." % ('are now' if value else 'are no longer'))
        return self.owner.db._hidden

    def can_see(self, target):
        if self.owner.account.is_admin():
            return True
        return not (target.time.is_dark() or target.time.is_hidden())




class CharacterAccount(object):

    def __init__(self, owner):
        self.owner = owner

    def reset_puppet_locks(self, player):
        """
        Called by the processes for binding a character to a player.
        """
        self.owner.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" % (self.owner.id, player.id))

    def is_admin(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Wizards)")

    def cost(self, update=None):
        if update is not None:
            try:
                new_value = int(update)
            except ValueError:
                raise ValueError("Character slots must be non-negative integers.")
            if new_value < 0:
                raise ValueError("Character slots must be non-negative integers.")
            self.owner.config.model.slot_cost = new_value
            self.owner.config.model.save(update_fields=['slot_cost'])
            self.owner.sys_msg("This Character is now worth %i Character Slots." % new_value)
        return self.owner.config.model.slot_cost

    def update_owner(self, player=None):
        if player:
            self.reset_puppet_locks(player)
            self.owner.config.model.player = player
            self.owner.config.model.save(update_fields=['player'])
        else:
            self.owner.locks.add("puppet:none()")
            self.owner.config.model.player = None
            self.owner.config.model.save(update_fields=['player'])

    def status(self):
        return 'Playable'

class CharacterConfig(object):

    def __init__(self, owner):
        self.owner = owner

class CharacterChannel(object):

    def __init__(self, owner):
        self.owner = owner

    def receive(self, channel, msg):
        pass


