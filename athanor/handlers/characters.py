import time, datetime
from athanor.utils.text import mxp
from athanor.utils.time import utcnow
from athanor.handlers.base import CharacterHandler
from athanor.models import CharacterCore
from athanor.utils.utils import import_property


class CharacterCoreHandler(CharacterHandler):
    key = 'core'
    style = 'fallback'
    system_name = 'SYSTEM'
    cmdsets = ('athanor.cmdsets.characters.CoreCharacterCmdSet', )
    django_model = CharacterCore

    def at_init(self):
        super(CharacterCoreHandler).at_init()
        if self.owner.sessions.count():
            self.base.systems['core'].register_character(self.owner)

    @property
    def last_login(self):
        return self.model.last_login

    @property
    def last_logout(self):
        return self.model.last_logout

    def at_post_unpuppet(self, account, session, **kwargs):
        session.msg(account.at_look(target=account, session=session))

    def at_object_creation(self):
        self.model.last_login = utcnow()
        self.model.last_logout = utcnow()
        self.model.save(update_fields=['last_login', 'last_logout'])

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
                session.account.unpuppet_object(session)

    @property
    def playtime(self):
        return self.model.playtime

    def update_playtime(self, seconds):
        self.model.playtime += datetime.timedelta(seconds)
        self.model.save(update_fields=['playtime'])

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

class CharacterCharacterHandler(CharacterHandler):
    key = 'character'
    style = 'account'
    system_name = 'ACCOUNT'

    @property
    def slot_cost(self):
        return 1


class CharacterMenuHandler(CharacterHandler):
    key = 'menu'
    style = 'account'
    system_name = 'SYSTEM'
    category = 'athanor'

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