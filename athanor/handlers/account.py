from __future__ import unicode_literals

import time, evennia, datetime
from django.conf import settings
from evennia import utils
from evennia.utils import time_format
from evennia.utils.ansi import ANSIString
from athanor.utils.time import utcnow

from athanor.handlers.base import AccountHandler
from athanor.settings.account import ACCOUNT_SYSTEM_SETTINGS


class AccountSystemHandler(AccountHandler):
    key = 'system'
    style = 'fallback'
    category = 'athanor_system'
    settings_classes = ACCOUNT_SYSTEM_SETTINGS
    system_name = 'SYSTEM'
    
    @property
    def base_character_slots(self):
        return settings.MAX_NR_CHARACTERS

    @property
    def extra_character_slots(self):
        return self.settings['extra_character_slots'].value

    @property
    def available_character_slots(self):
        return self.max_character_slots - self.base['characters'].used_slots()

    @property
    def max_character_slots(self):
        return self.base_character_slots + self.extra_character_slots

    def display(self, viewer, footer=True):
        message = list()
        message.append(viewer.render.subheader('Account: %s' % self.owner.key, style=self.style))
        message.append('Email: %s' % self.owner.email)
        message.append('Slots: %s/%s(%s)' % (self.available_character_slots, self.max_character_slots,
                                             self.extra_character_slots))
        chars = self.owner.characters.all()
        if chars:
            message.append(viewer.render.separator('Characters', style=self.style))
            char_table = viewer.render.make_table(['Name', 'Status', 'Cost'], width=[52, 20, 6], style=self.style)
            for char in chars:
                char_table.add_row(char.key, char.system.status(), char.system.cost())
            message.append(char_table)
        if footer:
            message.append(viewer.render.footer(style=self.style))
        return '\n'.join(unicode(line) for line in message)

    def is_builder(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Builder)")

    def is_admin(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Admin)")

    def is_developer(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Developer)")

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

    def change_password(self, enactor, old=None, new=None):
        if enactor.player == self.owner:
            if not self.owner.check_password(old):
                raise ValueError("The entered old-password was incorrect.")
        if not new:
            raise ValueError("No new password entered!")
        self.owner.set_password(new)
        self.owner.save()
        self.console_msg("Your password has been changed.")

    def change_email(self, enactor, new_email):
        fixed_email = evennia.AccountDB.objects.normalize_email(new_email)
        self.owner.email = fixed_email
        self.owner.save()
        self.console_msg("Your Account Email was changed to: %s" % fixed_email)

    def load(self):
        if self.owner.attributes.has(key='playtime', category=self.category):
            self.playtime = self.owner.attributes.get(key='playtime', category=self.category)
            return
        self.owner.attributes.add(key='playtime', value=0, category=self.category)
        self.playtime = self.owner.attributes.get(key='playtime', category=self.category)
        return

    def update_playtime(self, seconds):
        self.playtime += seconds

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
        tz = self['timezone']
        time = date.astimezone(tz)
        return time.strftime(format)

    def update_last_played(self):
        self.owner.attributes.add(key='lastplayed', value=int(utcnow().strftime('%s')), category=self.category)

    @property
    def last_played(self):
        if not self.owner.attributes.has(key='lastplayed', category=self.category):
            self.owner.attributes.add(key='lastplayed', value=int(utcnow().strftime('%s')), category=self.category)
        save_data = self.owner.attributes.get(key='lastplayed', category=self.category)
        return datetime.datetime.utcfromtimestamp(save_data)

    def off_or_idle_time(self):
        idle = self.owner.idle_time
        if idle is None:
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self):
        conn = self.owner.connection_time
        if conn is None:
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.owner.idle_time
        last = self.last_played
        if not idle:
            return viewer.ath['system'].display_time(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.owner.connection_time
        last = self.last_played
        if not conn:
            return viewer.ath['system'].display_time(date=last, format='%b %d')
        return time_format(conn, style=1)

    def can_see(self, target):
        if self.owner.system.is_admin():
            return True
        return not (target.system.dark() or target.system.hidden())





class AccountCharacterHandler(AccountHandler):
    style = 'account_appearance'
    key = 'characters'
    category = 'athanor_characters'
    
    def __init__(self, owner):
        super(AccountCharacterHandler, self).__init__(owner)
        self.character_list = list()
        self.load()
        
    def load(self):
        if not self.owner.attributes.has(key='character_list', category='athanor_settings'):
            self.owner.attributes.add(key='character_list', value=list(), category='athanor_settings')
        char_list = self.owner.attributes.get(key='character_list', category='athanor_settings')
        cleaned = sorted([char for char in char_list if char], key=lambda char: char.key)
        if len(char_list) != len(cleaned):
            self.owner.attributes.add(key='character_list', value=char_list, category='athanor_settings')
        self.character_list = cleaned
    
    def all(self):
        cleaned = sorted([char for char in self.character_list if char], key=lambda char: char.key)
        if len(cleaned) != len(self.character_list):
            self.owner.attributes.add(key='character_list', value=cleaned, category='athanor_settings')
            self.character_list = cleaned
        return cleaned
    
    def add(self, character):
        pass
    
    def remove(self, character):
        pass
        
    def create(self, name):
        pass

    def used_slots(self):
        return 0

class AccountLoginHandler(AccountHandler):
    key = 'login'
    category = 'athanor_login'
    style = 'login'

    def render_login(self, viewer):
        characters = self.base['characters'].all()
        message = list()
        message.append(viewer.styles.header("%s: Account Management" % settings.SERVERNAME, style=self.style))
        message += self.at_look_info_section(viewer)
        message += self.at_look_session_menu(viewer)
        message.append(viewer.styles.subheader('Commands', style=self.style))
        command_column = viewer.styles.make_table([], header=False, style=self.style)
        command_text = list()
        command_text.append(unicode(ANSIString(" |whelp|n - more commands")))
        if self.owner.db._reset_username:
            command_text.append(" |w@username <name>|n - Set your username!")
        if self.owner.db._reset_email or self.owner.email == 'dummy@dummy.com':
            command_text.append(" |w@email <address>|n - Set your email!")
        if self.owner.db._was_lost:
            command_text.append(" |w@penn <character>=<password>|n - Link an imported PennMUSH character.")
        command_text.append(" |w@charcreate <name> [=description]|n - create new character")
        command_text.append(" |w@ic <character>|n - enter the game (|w@ooc|n to get back here)")
        command_column.add_row("\n".join(command_text), width=80)
        message.append(command_column)
        if characters:
            message += self.at_look_character_menu(viewer)
        message.append(viewer.styles.subheader('Open Char Slots: %s/%s' % (
            self.base['system'].available_character_slots, self.base['system'].max_character_slots), style=self.style))
        self.owner.msg('\n'.join(unicode(line) for line in message))

    def at_look_info_section(self, viewer):
        message = list()
        info_column = viewer.styles.make_table([], header=False, style=self.style)
        info_text = list()
        info_text.append(unicode(ANSIString("Account:".rjust(8) + " |g%s|n" % (self.owner.key))))
        email = self.owner.email if self.owner.email != 'dummy@dummy.com' else '<blank>'
        info_text.append(unicode(ANSIString("Email:".rjust(8) + ANSIString(" |g%s|n" % email))))
        info_text.append(unicode(ANSIString("Perms:".rjust(8) + " |g%s|n" % ", ".join(self.owner.permissions.all()))))
        info_column.add_row("\n".join(info_text), width=80)
        message.append(info_column)
        return message

    def at_look_session_menu(self, viewer):
        sessions = self.owner.sessions.all()
        message = list()
        message.append(viewer.styles.subheader('Sessions', style=self.style))
        sesstable = viewer.styles.make_table(['ID', 'Protocol', 'Address', 'Connected'], width=[7, 23, 23, 27], style=self.style)
        for session in sessions:
            conn_duration = time.time() - session.conn_time
            sesstable.add_row(session.sessid, session.protocol_key,
                                isinstance(session.address, tuple) and str(session.address[0]) or str(
                                    session.address),
                                 utils.time_format(conn_duration, 0))
        message.append(sesstable)
        # message.append(separator())
        return message

    def at_look_character_menu(self, viewer):
        message = list()
        characters = self.owner.characters.all()
        message.append(viewer.styles.subheader('Characters', style=self.style))
        chartable = viewer.styles.make_table(['ID', 'Name', 'Type', 'Last Login'], width=[7, 37, 16, 20], style=self.style)
        for character in characters:
            login = character.character_settings.last_played
            if login:
                login = self.owner.time.display(date=login)
            else:
                login = 'N/A'
            type = character.config.model.character_type or 'N/A'
            chartable.add_row(character.id, character.key, type, login)
        message.append(chartable)
        # message.append(separator())
        return message


ALL = [AccountSystemHandler, AccountLoginHandler, AccountCharacterHandler]