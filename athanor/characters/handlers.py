import time
from athanor.utils.text import mxp
from athanor.utils.time import utcnow
from athanor.base.handlers import CharacterBaseHandler
from athanor.utils.utils import import_property


class CharacterCoreHandler(CharacterBaseHandler):
    key = 'core'
    style = 'fallback'
    system_name = 'SYSTEM'
    load_order = -1000
    cmdsets = ('athanor.characters.cmdsets.CoreCharacterCmdSet', )

    def at_init(self):
        super(CharacterCoreHandler).at_init()
        if self.owner.sessions.count():
            self.base.systems['core'].register_character(self.owner)

    @property
    def last_login(self):
        return self.get_db('last_login')

    @property
    def last_logout(self):
        return self.get_db('last_logout')

    def at_post_unpuppet(self, account, session, **kwargs):
        session.msg(account.at_look(target=account, session=session))

    def at_object_creation(self):
        self.set_db('last_login', utcnow())
        self.set_db('last_logout', utcnow())

    def at_post_puppet(self, **kwargs):
        self.set_db('last_login', utcnow())

    def at_true_logout(self, account, session, **kwargs):
        self.set_db('last_logout', utcnow())

    @property
    def last_played(self):
        return max(self.last_login, self.last_logout)

    def display_time(self, date=None, format=None):
        return self.account.ath['core'].display_time(date, format)

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

    def permission_rank(self):
        if self.is_developer():
            return 4
        if self.is_admin():
            return 3
        if self.is_builder():
            return 2
        return 1

    def can_modify(self, target):
        if not self.permission_rank() > 2:
            return False
        return self.permission_rank() > target.ath['core'].permission_rank()

    @property
    def account(self):
        return self.get_db('account')

    @account.setter
    def account(self, value):
        old_account = self.account
        if old_account:
            old_account.ath['character'].remove(self.owner)
        self.set_db('account', value)
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
        return bool(self.get_db('shelved'))

    @shelved.setter
    def shelved(self, value):
        self.set_db('shelved', value)

    @property
    def disabled(self):
        return bool(self.get_db('disabled'))

    @disabled.setter
    def disabled(self, value):
        self.set_db('disabled', value)

    @property
    def banned(self):
        data = self.get_db('banned')
        if data and data > utcnow():
            return data
        return False

    @banned.setter
    def banned(self, value):
        if not value:
            self.set_db('banned', False)
        else:
            self.set_db('banned', value)

    def disconnect(self, reason=None):
        """
        Disconnects all sessions from this character.

        :param reason: A string explaining the reason. This will be displayed to the character.
        :return:
        """
        if hasattr(self.owner, 'account'):
            self.console_msg("%s is being disconnected because: %s" % (self.owner, reason))
            for session in self.owner.sessions.get():
                session.account.unpuppet_object(session)

    @property
    def playtime(self):
        return self.get_db('playtime', 0)

    def update_playtime(self, seconds):
        self.set_db('playtime', self.playtime + seconds)

    @property
    def connection_time(self):
        if not self.owner.sessions.count():
            return -1
        count = min([sess.conn_time for sess in self.owner.sessions.get()])
        return time.time() - count

    @property
    def idle_time(self):
        sessions = self.owner.sessions.get()
        if sessions:
            return time.time() - min([ses.cmd_last for ses in sessions])
        return -1

    @property
    def timezone(self):
        return self.account.ath['core'].timezone

    @property
    def dark(self):
        return self.get_db('dark')

    @dark.setter
    def dark(self, value):
        self.set_db('dark', value)
        if value:
            self.console_msg("You are now Dark!")
        else:
            self.console_msg("You are no longer Dark!")


class CharacterCharacterHandler(CharacterBaseHandler):
    key = 'character'
    style = 'account'
    load_order = -999
    system_name = 'ACCOUNT'

    @property
    def slot_cost(self):
        return 1


class CharacterMenuHandler(CharacterBaseHandler):
    key = 'menu'
    system_name = 'SYSTEM'

    def load(self):
        self.menu = None
        self.menu_path = None

    def at_init(self):
        if self.menu:
            self.owner.cmdset.add(self.menu)

    def __getitem__(self, item):
        return self.data[item]

    def launch(self, path):
        """
        Add a Menu Cmdset.

        Args:
            path: Python path to a menu.

        Returns:
            None.

        """
        menu = import_property(path)
        self.menu_path = path
        self.owner.cmdset.add(menu)
        self.menu = menu


    def leave(self):
        if self.menu:
            self.owner.cmdset.remove(self.menu)

    def switch(self, path):
        """
        Shortcut for leaving one menu and starting up another!

        Args:
            path (str): Python path to a menu.

        Returns:
            None
        """
        self.leave()
        self.launch(path)


class CharacterChannelHandler(CharacterBaseHandler):
    key = 'channel'
    system_name = 'CHANNEL'

    def load(self):
        self.owner.ndb.channel_gags = set()
        if not self.owner.db.channel_colors:
            self.owner.db.channel_colors = dict()

    def send(self, channel, input):
        channel.speech(source=self.owner, text=input)

    def receive(self, channel, message, source=None):
        if channel in self.owner.ndb.channel_gags:
            return
        if not isinstance(message, basestring):
            message = message.render(viewer=self.owner)
        color = self.owner.db.channel_colors.get(channel, None) or channel['color'] or 'n'
        format_message = '[|%s%s|n] %s' % (color, channel.key, message)
        print format_message
        self.owner.msg(format_message)

    def join(self, channel):
        pass

    def leave(self, channel):
        pass

    def gag(self, channel):
        self.owner.ndb.channel_gags.add(channel)

    def ungag(self, channel):
        self.owner.ndb.channel_gags.remove(channel)
