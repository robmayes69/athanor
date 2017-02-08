from __future__ import unicode_literals

import time, evennia
from django.conf import settings
from evennia import utils
from evennia.utils import evtable
from evennia.utils import time_format
from evennia.utils.ansi import ANSIString
from athanor.utils.time import utcnow


class PlayerWeb(object):
    def __init__(self, owner):
        self.owner = owner

    def serialize(self, viewer):
        return {'id': self.owner.id, 'key': self.owner.key, 'conn': self.owner.connection_time,
                'idle': self.owner.idle_time,
                'conn_pretty': self.owner.who.off_or_conn_time(viewer),
                'idle_pretty': self.owner.who.last_or_idle_time(viewer)}

    def login_serialize(self):
        return {'id': self.owner.id, 'key': self.owner.key, 'admin': self.owner.is_admin()}


class PlayerTime(object):
    def __init__(self, owner):
        self.owner = owner
        self.config = owner.config

    def last_played(self, update=False):
        if update:
            self.config.update_last_played()
        return self.config.last_played

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
        last = self.config.last_played
        if not idle:
            return viewer.time.display(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.owner.connection_time
        last = self.config.last_played
        if not conn:
            return viewer.time.display(date=last, format='%b %d')
        return time_format(conn, style=1)

    def display(self, date=None, format=None):
        if not format:
            format = '%b %d %I:%M%p %Z'
        if not date:
            date = utcnow()
        tz = self.config['timezone']
        time = date.astimezone(tz)
        return time.strftime(format)


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
        if self.owner.is_admin():
            return True
        return not (target.who.is_dark() or target.who.is_hidden())




class PlayerAccount(object):

    def __init__(self, owner):
        self.owner = owner
        self.config = owner.config

    def display(self, viewer, footer=True):
        message = list()
        message.append(viewer.render.subheader('Account: %s' % self.owner.key))
        message.append('Email: %s' % self.owner.email)
        message.append('Slots: %s/%s(%s)' % (self.available_slots, self.max_slots, self.extra_slots))
        chars = self.characters()
        if chars:
            message.append(viewer.render.separator('Characters'))
            char_table = viewer.render.make_table(['Name', 'Status', 'Cost'], width=[52, 20, 6])
            for char in chars:
                char_table.add_row(char.key, char.account.status(), char.account.cost())
            message.append(char_table)
        if footer:
            message.append(viewer.render.footer())
        return '\n'.join(unicode(line) for line in message)

    def is_admin(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Wizards)")

    def is_immortal(self):
        return self.owner.locks.check_lockstring(self.owner, "dummy:perm(Immortals)")

    def characters(self):
        """
        Returns a list of all valid playable characters.
        """
        return sorted([setting.character for setting in self.owner.char_settings.filter(enabled=True)],
                      key=lambda char: char.key)

    def bind_character(self, character):
        """
        This method is used to attach a character to a player.

        Args:
            character (objectdb): The character being bound.
        """
        character.account.update_owner(self.owner)

    def unbind_character(self, character):
        character.account.update_owner(None)

    def disable(self, enactor=None):
        if enactor.player == self.owner:
            raise ValueError("Cannot disable yourself!")

        self.config.model.enabled = False
        self.config.model.save(update_fields=['enabled'])
        self.owner.sys_msg("Your account has been disabled!", sys_name='ACCOUNT')
        for session in self.owner.sessions.all():
            self.owner.disconnect_session_from_player(session)

    def enable(self, enactor=None):
        self.config.model.enabled = True
        self.config.model.save(update_fields=['enabled'])

    def change_password(self, enactor, old=None, new=None):
        if enactor.player == self.owner:
            if not self.owner.check_password(old):
                raise ValueError("The entered old-password was incorrect.")
        if not new:
            raise ValueError("No new password entered!")
        self.owner.set_password(new)
        self.owner.save()
        self.owner.sys_msg("Your password has been changed.", sys_name='ACCOUNT')

    def change_email(self, new_email):
        fixed_email = evennia.PlayerDB.objects.normalize_email(new_email)
        self.owner.email = fixed_email
        self.owner.save()
        self.owner.sys_msg("Your Account Email was changed to: %s" % fixed_email)

    @property
    def available_slots(self):
        return self.max_slots - self.used_slots

    @property
    def max_slots(self):
        return self.base_slots + self.extra_slots

    @property
    def base_slots(self):
        return settings.MAX_NR_CHARACTERS

    @property
    def extra_slots(self):
        return self.config.model.extra_slots

    @property
    def used_slots(self):
        return sum(self.owner.char_settings.filter(enabled=True).values_list('slot_cost', flat=True))

    def set_slots(self, value):
        try:
            value = int(value)
        except ValueError:
            raise ValueError("Slots must be set to a whole number!")
        self.config.model.extra_slots = value
        self.config.model.save(update_fields=['extra_slots'])


class PlayerRender(object):
    def __init__(self, owner):
        self.owner = owner
        self.config = owner.config
        self.cache = dict()

    def render_login(self, session=None):
        characters = self.owner.account.characters()
        message = list()
        message.append(self.header("%s: Account Management" % settings.SERVERNAME))
        message += self.at_look_info_section()
        message += self.at_look_session_menu()
        message.append(self.subheader('Commands'))
        command_column = self.make_table([], header=False)
        command_text = list()
        command_text.append(unicode(ANSIString(" {whelp{n - more commands")))
        if self.owner.db._reset_username:
            command_text.append(" {w@username <name>{n - Set your username!")
        if self.owner.db._reset_email or self.owner.email == 'dummy@dummy.com':
            command_text.append(" {w@email <address>{n - Set your email!")
        if self.owner.db._was_lost:
            command_text.append(" {w@penn <character>=<password>{n - Link an imported PennMUSH character.")
        command_text.append(" {w@charcreate <name> [=description]{n - create new character")
        command_text.append(" {w@ic <character>{n - enter the game ({w@ooc{n to get back here)")
        command_column.add_row("\n".join(command_text), width=80)
        message.append(command_column)
        if characters:
            message += self.at_look_character_menu()

        message.append(self.subheader('Open Char Slots: %s/%s' % (
            self.owner.account.available_slots, self.owner.account.max_slots)))
        self.owner.msg('\n'.join(unicode(line) for line in message))


    def at_look_info_section(self, viewer=None):
        if not viewer:
            viewer = self
        message = list()
        info_column = self.make_table([], header=False)
        info_text = list()
        info_text.append(unicode(ANSIString("Account:".rjust(8) + " {g%s{n" % (self.owner.key))))
        email = self.owner.email if self.owner.email != 'dummy@dummy.com' else '<blank>'
        info_text.append(unicode(ANSIString("Email:".rjust(8) + ANSIString(" {g%s{n" % email))))
        info_text.append(unicode(ANSIString("Perms:".rjust(8) + " {g%s{n" % ", ".join(self.owner.permissions.all()))))
        info_column.add_row("\n".join(info_text), width=80)
        message.append(info_column)
        return message

    def at_look_session_menu(self):
        sessions = self.owner.sessions.all()
        message = list()
        message.append(self.subheader('Sessions'))
        sesstable = self.make_table(['ID', 'Protocol', 'Address', 'Connected'], width=[7, 22, 22, 27])
        for session in sessions:
            conn_duration = time.time() - session.conn_time
            sesstable.add_row(session.sessid, session.protocol_key,
                                isinstance(session.address, tuple) and str(session.address[0]) or str(
                                    session.address),
                                 utils.time_format(conn_duration, 0))
        message.append(sesstable)
        # message.append(separator())
        return message

    def at_look_character_menu(self):
        message = list()
        characters = self.owner.account.characters()
        message.append(self.subheader('Characters'))
        chartable = self.make_table(['ID', 'Name', 'Type', 'Last Login'], width=[7, 36, 15, 20])
        for character in characters:
            login = character.character_settings.last_played
            if login:
                login = self.owner.time.display(date=login)
            else:
                login = 'N/A'
            chartable.add_row(character.id, character.key, '', login)
        message.append(chartable)
        # message.append(separator())
        return message

    def make_table(self, names, border='cols', header=True, **kwargs):
        border_color = self.config['border_color']
        column_color = self.config['column_color']

        colornames = ['{%s%s{n' % (column_color, name) for name in names]
        header_line_char = ANSIString('{%s-{n' % border_color)
        corner_char = ANSIString('{%s+{n' % border_color)
        border_left_char = ANSIString('{%s|{n' % border_color)
        border_right_char = ANSIString('{%s|{n' % border_color)
        border_bottom_char = ANSIString('{%s-{n' % border_color)
        border_top_char = ANSIString('{%s-{n' % border_color)

        table = evtable.EvTable(*colornames, border=border, pad_width=0, valign='t', header_line_char=header_line_char,
                                corner_char=corner_char, border_left_char=border_left_char,
                                border_right_char=border_right_char, border_bottom_char=border_bottom_char,
                                border_top_char=border_top_char, header=header)

        if "width" in kwargs:
            for count, width in enumerate(kwargs['width']):
                table.reformat_column(count, width=width)
        return table

    def header(self, header_text=None, fill_character=None, edge_character=None, mode='header', color_header=True):
        key = (header_text, mode, edge_character)
        if key in self.cache.keys():
            return self.cache[key]
        colors = {}
        colors['border'] = self.config['border_color']
        colors['headertext'] = self.config['headertext_color']
        colors['headerstar'] = self.config['headerstar_color']
        width = 80
        if edge_character:
            width -= 2

        if header_text:
            if color_header:
                header_text = ANSIString(header_text).clean()
                header_text = ANSIString('|n|%s%s|n' % (colors['headertext'], header_text))
            if mode == 'header':
                begin_center = ANSIString("|n|%s<|%s* |n" % (colors['border'], colors['headerstar']))
                end_center = ANSIString("|n |%s*|%s>|n" % (colors['headerstar'], colors['border']))
                center_string = ANSIString(begin_center + header_text + end_center)
            else:
                center_string = ANSIString('|n |%s%s |n' % (colors['headertext'], header_text))
        else:
            center_string = ''

        if not fill_character and mode in ['header', 'footer']:
            fill_character = '='
        elif not fill_character and mode == 'subheader':
            fill_character = '='
        elif not fill_character:
            fill_character = '-'
        fill = ANSIString('|n|%s%s|n' % (colors['border'], fill_character))

        if edge_character:
            edge_fill = ANSIString('|n|%s%s|n' % (colors['border'], edge_character))
            main_string = ANSIString(center_string).center(width, fill)
            final_send = ANSIString(edge_fill) + ANSIString(main_string) + ANSIString(edge_fill)
        else:
            final_send = ANSIString(center_string).center(width, fill)
        self.cache[key] = final_send
        return final_send

    def subheader(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'subheader'
        return self.header(*args, **kwargs)

    def separator(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'separator'
        return self.header(*args, **kwargs)

    def footer(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'footer'
        return self.header(*args, **kwargs)

    def clear_cache(self):
        self.cache = dict()

class ColorHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.models = {'groups': owner.group_colors, 'channels': owner.channel_colors,
                       'characters': owner.char_colors}
        for key in self.models.keys():
            data = {dat.target: dat.color for dat in self.models[key].all()}
            setattr(self, key, data)

    def set(self, target=None, value=None, mode='characters'):
        model = self.models[mode]
        if not target:
            raise ValueError("Nothing entered to set!")
        if not value:
            return self.clear(target, mode)
        if len(ANSIString('|%s|n' % value)):
            raise ValueError("You must enter a valid color code!")
        data = getattr(self, mode)
        data[target] = value
        dat, created = model.get_or_create(target=target)
        dat.color = value
        dat.save()
        return "You will now see %s as |%s%s|n!" % (target, value, target)

    def clear(self, target, mode):
        if target in getattr(self, mode).keys():
            data = getattr(self, mode)
            del data[target]
        else:
            raise ValueError("Cannot clean an entry you don't have!")
        model = self.models[mode]
        model.objects.filter(target=target).delete()
        return "Custom color for %s cleared." % target