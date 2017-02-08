from __future__ import unicode_literals

from evennia.utils import time_format
from athanor.classes.channels import PublicChannel


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


class CharacterChannel(object):

    def __init__(self, owner):
        self.owner = owner
        self.gagging = list()
        self.monitor = False

    def receive(self, channel, speech, emit=False):
        if channel in self.gagging:
            return
        if not hasattr(self.owner, 'player'):
            return
        prefix = self.prefix(channel)
        if emit:
            self.owner.msg('%s %s' % (prefix, speech))
            return
        if self.monitor:
            render = speech.monitor_display(self.owner)
        else:
            render = speech.render(self.owner)
        self.owner.msg('%s %s' % (prefix, render))

    def color_name(self, channel):
        color = self.owner.player.colors.channels.get(channel, None)
        if not color:
            color = channel.db.color
        if not color:
            color = 'n'
        return '|%s%s|n' % (color, channel.key)

    def prefix(self, channel):
        return '<%s>' % self.color_name(channel)

    def status(self, channel):
        if not channel.has_connection(self.owner):
            return 'Off'
        if channel in self.gagging:
            return 'Gag'
        return 'On'

    def visible(self):
        channels = PublicChannel.objects.all().order_by('db_key')
        return [chan for chan in channels if chan.locks.check(self.owner, 'listen')]


class CharacterPage(object):

    def __init__(self, owner):
        self.owner = owner
        self.last_to = list()
        self.reply_to = list()

    def send(self, targets, msg):
        targets.discard(self.owner)
        self.last_to = targets
        for target in targets:
            target.page.receive(targets, msg, source=self.owner)
        outpage = self.owner.player_config['outpage_color']
        self.owner.msg('|%sPAGE:|n %s' % (outpage, msg.render(viewer=self.owner)))


    def receive(self, recipients, msg, source=None):
        color = self.owner.player_config['page_color']
        self.owner.msg('|%sPAGE:|n %s' % (color, msg.render(viewer=self.owner)))
        reply = set(recipients)
        reply.add(source)
        reply.discard(self.owner)
        self.reply_to = reply

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