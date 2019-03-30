import time
from django.conf import settings
from evennia import utils
from evennia.utils.ansi import ANSIString
from athanor.utils.time import utcnow
from athanor.utils.utils import import_property
from athanor.utils.text import partial_match
from athanor.base.handlers import AccountBaseHandler
from athanor import AthException, STYLES_DATA


class AccountCoreHandler(AccountBaseHandler):
    key = 'core'
    category = 'athanor'
    load_order = -1000
    system_name = 'ACCOUNT'
#    cmdsets = ('athanor.accounts.cmdsets.OOCCmdSet', 'athanor.base.original_cmdsets.AccountAdminCmdSet',
#               'athanor.base.original_cmdsets.AccountBaseCmdSet')
    settings_data = (
        ('timezone', "Your choice of Timezone", 'timezone', 'UTC'),
    )

    def at_account_creation(self):
        self.set_db('last_login', utcnow())
        self.set_db('last_logout', utcnow())

    def at_post_login(self, session, **kwargs):
        self.set_db('last_login', utcnow())
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

    def display_time(self, date=None, format=None):
        """
        Displays a DateTime in a localized timezone to the account.

        :param date: A datetime object. Will be utcnow() if not provided.
        :param format: a strftime formatter.
        :return: Time as String
        """
        if not format:
            format = '%b %d %I:%M%p %Z'
        if not date:
            date = utcnow()
        tz = self.timezone
        time = date.astimezone(tz)
        return time.strftime(format)

    @property
    def timezone(self):
        return self['timezone']

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
    def last_played(self):
        return max(self.last_login, self.last_logout)

    @property
    def last_login(self):
        return self.get_db('last_login')

    @property
    def last_logout(self):
        return self.get_db('last_logout')

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


class AccountCharacterHandler(AccountBaseHandler):
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
        return settings.ATHANOR_CHARACTER_SLOTS

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

    def render_login(self, session, viewer):
        characters = self.base['character'].all()
        message = list()
        message.append(session.ath['render'].header("%s: Account Management" % settings.SERVERNAME))
        message += self.at_look_info_section(session, viewer)
        message += self.at_look_session_menu(session, viewer)
        message.append(session.ath['render'].subheader('Commands'))
        command_column = session.ath['render'].table([], header=False)
        command_text = list()
        command_text.append(str(ANSIString(" |whelp|n - more commands")))
        if self.owner.db._reset_username:
            command_text.append(" |w@username <name>|n - Set your username!")
        if self.owner.db._reset_email or self.owner.email == 'dummy@dummy.com':
            command_text.append(" |w@email <address>|n - Set your email!")
        if self.owner.db._was_lost:
            command_text.append(" |w@penn <character>=<password>|n - Link an imported PennMUSH character.")
        command_text.append(" |w@charcreate <name> [=description]|n - create new character")
        command_text.append(" |w@ic <character>|n - enter the game (|w@ooc|n to get back here)")
        command_column.add_row("\n".join(command_text))
        message.append(command_column)
        if characters:
            message += self.at_look_character_menu(session, viewer)
        message.append(session.ath['render'].subheader('Open Char Slots: %s/%s' % (
            self.available_character_slots, self.max_character_slots)))
        return '\n'.join(str(line) for line in message if line)

    def at_look_info_section(self, session, viewer):
        message = list()
        info_column = session.ath['render'].table((), header=False)
        info_text = list()
        info_text.append(str(ANSIString("Account:".rjust(8) + " |g%s|n" % (self.owner.key))))
        email = self.owner.email if self.owner.email != 'dummy@dummy.com' else '<blank>'
        info_text.append(str(ANSIString("Email:".rjust(8) + ANSIString(" |g%s|n" % email))))
        info_text.append(str(ANSIString("Perms:".rjust(8) + " |g%s|n" % ", ".join(self.owner.permissions.all()))))
        info_column.add_row("\n".join(info_text))
        message.append(info_column)
        return message

    def at_look_session_menu(self, session, viewer):
        sessions = self.owner.sessions.all()
        message = list()
        message.append(session.ath['render'].subheader('Sessions'))
        columns = (('ID', 7, 'l'), ('Protocol', 0, 'l'), ('Address', 0, 'l'), ('Connected', 0, 'l'))
        sesstable = session.ath['render'].table(columns)
        for session in sessions:
            conn_duration = time.time() - session.conn_time
            sesstable.add_row(session.sessid, session.protocol_key,
                                isinstance(session.address, tuple) and str(session.address[0]) or str(
                                    session.address),
                                 utils.time_format(conn_duration, 0))
        message.append(sesstable)
        return message

    def at_look_character_menu(self, session, viewer):
        message = list()
        characters = self.base['character'].all()
        message.append(session.ath['render'].subheader('Characters'))
        columns = (('ID', 7, 'l'), ('Name', 0, 'l'), ('Type', 0, 'l'), ('Last Login', 0, 'l'))
        chartable = session.ath['render'].table(columns)
        for character in characters:
            login = character.ath['core'].last_played
            if login:
                login = self.owner.ath['core'].display_time(date=login)
            else:
                login = 'N/A'
            type = 'N/A'
            chartable.add_row(character.id, character.key, type, login)
        message.append(chartable)
        return message


class AccountMenuHandler(AccountBaseHandler):
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


class AccountColorHandler(AccountBaseHandler):
    key = 'color'
    system_name = 'COLOR'

    @property
    def settings_data(self):
        data = list()
        for k, v in STYLES_DATA.items():
            data.append((k, v[1], v[0], v[2]))
        return tuple(data)

    def get_settings(self):
        if not self.loaded_settings:
            self.load_settings()
        return self.settings


class AccountChannelHandler(AccountBaseHandler):
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
