from __future__ import unicode_literals

from evennia.utils import time_format
from athanor.classes.channels import PublicChannel
from athanor.managers import ALL_MANAGERS
from athanor.utils.text import mxp
from athanor.utils.time import utc_from_string
from athanor.utils.handlers.account import AccountStyles, AccountRender
from athanor.core.config.settings_templates import __SettingManager
from athanor.core.config.character_settings import CHARACTER_SYSTEM_SETTINGS
from athanor.utils.time import utcnow

class __CharacterManager(__SettingManager):
    pass


class CharacterSystem(__CharacterManager):
    setting_classes = CHARACTER_SYSTEM_SETTINGS
    style = 'fallback'
    system_name = 'SYSTEM'

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
        self.settings_dict['last_played'].set(utcnow(), [], self.owner)

    @property
    def last_played(self):
        return self['last_played']

    def off_or_idle_time(self, viewer):
        idle = self.owner.idle_time
        if idle is None or not viewer.system.can_see(self.owner):
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self, viewer):
        conn = self.owner.connection_time
        if conn is None or not viewer.system.can_see(self.owner):
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.owner.idle_time
        last = self.last_played()
        if not idle or not viewer.system.can_see(self.owner):
            return viewer.time.display(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.owner.connection_time
        last = self.last_played()
        if not conn or not viewer.time.can_see(self.owner):
            return viewer.time.display(date=last, format='%b %d')
        return time_format(conn, style=1)

    def display_time(self, date=None, format=None):
        return self.account.system.display_time(date, format)

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

    def status(self):
        return 'Playable'


class CharacterChannel(__CharacterManager):

    def __init__(self, owner):
        super(CharacterChannel, self).__init__(owner)
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


class CharacterPage(__CharacterManager):
    style = 'page'
    system_name = 'PAGE'
    key = 'page'

    def __init__(self, owner):
        super(CharacterPage, self).__init__(owner)
        self.last_to = list()
        self.reply_to = list()

    def send(self, targets, msg):
        targetnames = ', '.join([str(tar) for tar in targets])
        targets.discard(self.owner)
        self.last_to = targets
        for target in targets:
            target.page.receive(targets, msg, source=self.owner)
        outpage = self.owner.player_config['outpage_color']
        self.owner.msg('|%sPAGE|n (%s)|%s:|n %s' % (outpage, targetnames, outpage, msg.render(viewer=self.owner)))


    def receive(self, recipients, msg, source=None):
        color = self.owner.player_config['page_color']
        others = set(recipients)
        others.discard(self.owner)
        othernames = ', '.join([str(oth) for oth in others])
        if othernames:
            extra = ', to %s' % othernames
        else:
            extra = ''
        self.owner.msg('|%sPAGE (from %s%s):|n %s' % (color, source, extra, msg.render(viewer=self.owner)))
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

class CharacterBBS(__CharacterManager):
    style = 'bbs'
    key = 'bbs'
    system_name = 'BBS'

    def __init__(self, owner):
        super(CharacterBBS, self).__init__(owner)
        self.manager = ALL_MANAGERS.board

    def join_board(self, enactor, name=None):
        board = self.manager.find_board(name=name, checker=self.owner, visible_only=False)
        board.character_join(self.owner)

    def leave_board(self, enactor, name=None):
        board = self.manager.find_board(name=name, checker=self.owner, visible_only=True)
        board.character_leave(self.owner)

    def message_alert(self, post):
        command = '+bbread %s/%s' % (post.board.alias, post.order)
        command = mxp(text=command, command=command)
        if post.anonymous:
            source = post.board.anonymous if post.board.anonymous else 'Anonymous'
            if self.owner.accountsub.is_admin():
                source = '%s (%s)' % (source, post.owner)
        else:
            source = post.owner
        self.sys_msg("New BB Message (%s) posted to '%s' by %s: %s" % (command, post.board, source, post.subject))


class CharacterStyles(AccountStyles):
    pass


class CharacterRender(AccountRender):
    pass