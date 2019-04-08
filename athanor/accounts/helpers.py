import time
from django.conf import settings
from evennia import utils
from evennia.utils.ansi import ANSIString
from athanor.utils.time import utcnow
from athanor.utils.utils import import_property
from athanor.utils.text import partial_match
from athanor.base.helpers import AccountBaseHelper
from athanor import AthException, STYLES_DATA
from athanor.models import AccountPlaytime


class AccountCoreHelper(AccountBaseHelper):
    key = 'core'
    category = 'athanor'
    load_order = -1000
    system_name = 'ACCOUNT'
#    cmdsets = ('athanor.accounts.cmdsets.OOCCmdSet', 'athanor.base.original_cmdsets.AccountAdminCmdSet',
#               'athanor.base.original_cmdsets.AccountBaseCmdSet')
    settings_data = (
        ('timezone', "Your choice of Timezone", 'timezone', 'UTC'),
    )

    def at_post_login(self, session, **kwargs):
        self.base.systems['account'].add_online(self.owner)

    def at_true_logout(self, account, session, **kwargs):
        self.set_db('last_logout', utcnow())
        self.base.systems['account'].remove_online(self.owner)

    def is_builder(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Builder)")

    def is_admin(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Admin)")

    def is_developer(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Developer)")

    def is_superuser(self):
        return self.owner.is_superuser

    def status_name(self):
        if self.owner.is_superuser:
            return 'Superuser'
        if self.is_developer():
            return 'Developer'
        if self.is_admin():
            return 'Admin'
        if self.is_builder():
            return 'Builder'
        return 'Mortal'

    def permission_rank(self):
        if self.is_superuser():
            return 5
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
        return (self.permission_rank() > target.ath['core'].permission_rank()) or self.is_superuser()



    @property
    def timezone(self):
        return self['timezone']

    @property
    def disabled(self):
        return bool(self.get_db('disabled'))

    @disabled.setter
    def disabled(self, value):
        self.set_db('disabled', value)
        if value:
            self.disconnect()

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
            self.disconnect()

    def disconnect(self):
        sessions = self.owner.sessions.all()
        if not sessions:
            return
        self.owner.unpuppet_all()
        from evennia import SESSION_HANDLER
        for session in sessions:
            SESSION_HANDLER.sessions.disconnect(session)

    @property
    def playtime(self):
        return self.get_db('playtime', 0)

    def update_playtime(self, seconds):
        self.set_db('playtime', self.playtime + seconds)
        all_chars = self.base['character'].all()
        for char in [sess.puppet for sess in self.owner.sessions.all() if sess.puppet]:
            char.ath['core'].update_playtime(seconds)
            self.update_playtime_character(char, seconds)

    @property
    def playtime_characters(self):
        return self.get_db('playtime_characters', dict())

    def update_playtime_character(self, character, seconds):
        data = self.playtime_characters
        data[character] = data.get(character, 0) + seconds
        self.set_db('playtime_characters', data)



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


class AccountPlaytimeHelper(AccountBaseHelper):
    key = 'playtime'
    system_name = 'PLAYTIME'
    load_order = -900
    interval = 60

    def at_true_login(self, session, **kwargs):
        playtime = AccountPlaytime.objects.create(account=self.owner, login_time=utcnow())

    def at_true_logout(self, session, **kwargs):
        AccountPlaytime.objects.filter(account=self.owner, logout_time__isnull=True).update(logout_time=utcnow())

    @property
    def last_played(self):
        return max(self.last_login, self.last_logout)

    @property
    def last_login(self):
        return self.owner.playtime.order_by('login_time').first().login_time

    @property
    def last_logout(self):
        return self.owner.playtime.filter(logout_time__isnull=False).order_by('logout_time').first().logout_time


class AccountCharacterHelper(AccountBaseHelper):
    key = 'character'
    load_order = -999
    system_name = 'ACCOUNT'

    def at_post_login(self, session, **kwargs):
        session.msg(self.owner.at_look(session=session, target=self.owner))

    def all(self):
        return self.get_db('characters', [])

    def add(self, character):
        characters = self.all()
        characters.append(character)
        character.ath['core'].account = self.owner
        self.set_db('characters', [char for char in characters if char])

    def remove(self, character):
        characters = self.all()
        characters.remove(character)
        self.set_db('characters', [char for char in characters if char])

    @property
    def slot_cost(self):
        return 1

    def login_data(self):
        return tuple([(char.id, char.key) for char in self.all()])

    @property
    def base_character_slots(self):
        return settings.MAX_NR_CHARACTERS

    @property
    def extra_character_slots(self):
        return self.get_db('extra_slots', 0)

    @extra_character_slots.setter
    def extra_character_slots(self, value):
        self.set_db('extra_slots', value)

    @property
    def available_character_slots(self):
        return self.max_character_slots - sum([char.ath['character'].slot_cost for char in self.all()])

    @property
    def max_character_slots(self):
        return self.base_character_slots + self.extra_character_slots




class AccountMenuHelper(AccountBaseHelper):
    key = 'menu'
    system_name = 'SYSTEM'

    def load(self):
        self.menu = None
        if not self.owner.attributes.has(key='%s_current', category=self.category):
            self.owner.attributes.add(key='%s_current', category=self.category, value=None)
        self.menu_path = self.owner.attributes.get(key='%s_current', category=self.category)
        if not self.owner.attributes.has(key=self.key, category=self.category):
            self.owner.attributes.add(key=self.key, category=self.category, value={})
        self.data = self.owner.attributes.get(key=self.key, category=self.category)
        if self.menu_path:
            self.menu = import_property(self.menu_path)

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


class AccountChannelHelper(AccountBaseHelper):
    key = 'channel'
    system_name = 'CHANNEL'

    def load(self):
        self.owner.ndb.channel_gags = set()

    def colors(self):
        if not self.owner.db.channel_colors:
            self.owner.db.channel_colors = dict()
        return self.owner.db.channel_colors

    def send(self, channel, in_text):
        channel.speech(source=self.owner, text=in_text)

    def receive(self, channel, message, source=None):
        if channel in self.owner.ndb.channel_gags:
            return
        if not isinstance(message, str):
            message = message.render(viewer=self.owner)
        color = self.colors().get(channel, None) or channel['color'] or 'n'
        format_message = '[|%s%s|n] %s' % (color, channel.key, message)
        print(format_message)
        self.owner.msg(format_message)

    def join(self, channel):
        results = channel.connect(self.owner)
        return results

    def leave(self, channel):
        results = channel.disconnect(self.owner)
        return results

    def gag(self, channel):
        self.owner.ndb.channel_gags.add(channel)
        channel.mute(self.owner)

    def ungag(self, channel):
        self.owner.ndb.channel_gags.remove(channel)
        channel.unmute(self.owner)

    def gag_all(self):
        for channel in self.all():
            self.gag(channel)

    def ungag_all(self):
        for channel in self.owner.ndb.channel_gags:
            self.ungag(channel)

    def all(self):
        return [chan for chan in self.base.systems['channel'].all() if chan.access(self.owner, 'listen')]

    def search(self, find):
        found = partial_match(find, self.all())
        if not found:
            raise AthException("Could not find Channel named '%s'" % find)
        return found
