from __future__ import unicode_literals

import time, evennia, datetime
from django.conf import settings
from evennia import utils
from evennia.utils import time_format
from evennia.utils.ansi import ANSIString
from athanor.utils.time import utcnow
from athanor.models import AccountSettings

from athanor.handlers.base import AccountHandler


class AccountSystemHandler(AccountHandler):
    key = 'system'
    style = 'fallback'
    category = 'athanor'
    system_name = 'SYSTEM'
    cmdsets = ('athanor.cmdsets.accounts.AccountSystemCmdSet', )

    def __init__(self, base):
        super(AccountSystemHandler, self).__init__(base)
        self.model, created = AccountSettings.objects.get_or_create(account=self)

    def at_post_login(self, session, **kwargs):
        self.model.last_login = utcnow()
        self.model.save(update_fields=['last_login'])

    def at_true_logout(self, account, session, **kwargs):
        self.model.last_logout = utcnow()
        self.model.save(update_fields=['last_logout'])

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

    @property
    def timezone(self):
        return self.model.timezone

    @timezone.setter
    def timezone(self, value):
        self.model.timezone = value
        self.model.save(update_fields=['timezone',])

    @property
    def shelved(self):
        return self.model.shelved

    @shelved.setter
    def shelved(self, value):
        self.model.shelved = value
        self.model.save(update_fields=['shelved', ])

    @property
    def disabled(self):
        return self.model.disabled

    @disabled.setter
    def disabled(self, value):
        self.model.disabled = value
        self.model.save(update_fields=['disabled', ])

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
        self.model.save(update_fields=['banned', ])

    @property
    def playtime(self):
        return self.model.playtime

    def update_playtime(self, seconds):
        self.model.playtime += datetime.timedelta(seconds)
        self.model.save(update_fields=['playtime'])

    @property
    def last_played(self):
        return max(self.model.last_login, self.model.last_logout)


class AccountWhoHandler(AccountHandler):
    key = 'who'
    style = 'who'
    category = 'athanor'
    system_name = 'WHO'

    def __init__(self, base):
        super(AccountWhoHandler, self).__init__(base)
        self.model, created = AccountSettings.objects.get_or_create(account=self)

    def off_or_idle_time(self):
        idle = self.idle_time
        if idle is None:
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self):
        conn = self.connection_time
        if conn is None:
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.idle_time
        last = self.base['system'].last_played
        if not idle:
            return viewer.ath['system'].display_time(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.connection_time
        last = self.base['system'].last_played
        if not conn:
            return viewer.ath['system'].display_time(date=last, format='%b %d')
        return time_format(conn, style=1)

    def can_see(self, target):
        if self.owner.system.is_admin():
            return True
        return not (target.system.dark() or target.system.hidden())

    @property
    def hidden(self):
        return self.model.hidden

    @hidden.setter
    def hidden(self, value):
        self.model.hidden = value
        self.model.save(update_fields=['hidden', ])

    @property
    def dark(self):
        return self.model.dark

    @dark.setter
    def dark(self, value):
        self.model.dark = value
        self.model.save(update_fields=['dark', ])

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


class AccountCharacterHandler(AccountHandler):
    key = 'character'
    style = 'account'
    category = 'athanor'
    system_name = 'ACCOUNT'
    
    def __init__(self, base):
        super(AccountCharacterHandler, self).__init__(base)
        self.model, created = AccountSettings.objects.get_or_create(account=self)
    
    def all(self):
        return self.model.characters.all().order_by('db_key')

    def add(self, character):
        self.model.characters.add(character)
        character.ath['character'].account = self.owner
    
    def remove(self, character):
        self.model.characters.remove(character)
        character.ath['character'].account = None

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
        return self.model.extra_character_slots

    @extra_character_slots.setter
    def extra_character_slots(self, value):
        self.model.extra_character_slots = value
        self.model.save(update_fields=['extra_character_slots', ])

    @property
    def available_character_slots(self):
        return self.max_character_slots - sum([char.ath['character'].slot_cost for char in self.all()])

    @property
    def max_character_slots(self):
        return self.base_character_slots + self.extra_character_slots

    def render_login(self, session, viewer):
        characters = self.base['character'].all()
        message = list()
        message.append(session.render.header("%s: Account Management" % settings.SERVERNAME, style=self.style))
        message += self.at_look_info_section(session, viewer)
        message += self.at_look_session_menu(session, viewer)
        message.append(session.render.subheader('Commands', style=self.style))
        command_column = session.render.table([], header=False, style=self.style)
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
            message += self.at_look_character_menu(session, viewer)
        message.append(session.render.subheader('Open Char Slots: %s/%s' % (
            self.available_character_slots, self.max_character_slots), style=self.style))
        return '\n'.join(unicode(line) for line in message if line)

    def at_look_info_section(self, session, viewer):
        message = list()
        info_column = session.render.table((), header=False, style=self.style)
        info_text = list()
        info_text.append(unicode(ANSIString("Account:".rjust(8) + " |g%s|n" % (self.owner.key))))
        email = self.owner.email if self.owner.email != 'dummy@dummy.com' else '<blank>'
        info_text.append(unicode(ANSIString("Email:".rjust(8) + ANSIString(" |g%s|n" % email))))
        info_text.append(unicode(ANSIString("Perms:".rjust(8) + " |g%s|n" % ", ".join(self.owner.permissions.all()))))
        info_column.add_row("\n".join(info_text))
        message.append(info_column)
        return message

    def at_look_session_menu(self, session, viewer):
        sessions = self.owner.sessions.all()
        message = list()
        message.append(session.render.subheader('Sessions', style=self.style))
        columns = (('ID', 7, 'l'), ('Protocol', 23, 'l'), ('Address', 23, 'l'), ('Connected', 27, 'l'))
        sesstable = session.render.table(columns, style=self.style)
        for session in sessions:
            conn_duration = time.time() - session.conn_time
            sesstable.add_row(session.sessid, session.protocol_key,
                                isinstance(session.address, tuple) and str(session.address[0]) or str(
                                    session.address),
                                 utils.time_format(conn_duration, 0))
        message.append(sesstable)
        # message.append(separator())
        return message

    def at_look_character_menu(self, session, viewer):
        message = list()
        characters = self.owner.ath['character'].all()
        message.append(session.render.subheader('Characters', style=self.style))
        columns = (('ID', 7, 'l'), ('Name', 37, 'l'), ('Type', 16, 'l'), ('Last Login', 20, 'l'))
        chartable = session.render.table(columns, style=self.style)
        for character in characters:
            login = character.ath['system'].last_played
            if login:
                login = self.owner.ath['system'].display_time(date=login)
            else:
                login = 'N/A'
            type = 'N/A'
            chartable.add_row(character.id, character.key, type, login)
        message.append(chartable)
        # message.append(separator())
        return message