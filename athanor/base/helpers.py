import math, time
from evennia.utils.ansi import ANSIString
from evennia.utils.evtable import EvTable
from athanor import AthException
from athanor.utils.text import partial_match
from athanor.utils.time import utcnow


class BaseHelper(object):
    key = 'base'
    cmdsets = ()
    load_order = 0
    settings_data = tuple()
    extra_settings_data = tuple()
    category = 'athanor'
    system_name = 'SYSTEM'

    def __init__(self, base):
        self.base = base
        self.owner = base.owner
        self.loaded_settings = False
        self.settings = dict()
        self.load_cmdsets()
        self.load()

    def get_settings_data(self):
        return self.settings_data + self.extra_settings_data

    def load_settings(self):
        saved_data = dict(self.get_db('settings', dict()))
        for setting_def in self.get_settings_data():
            new_setting = self.base.settings[setting_def[2]](self, setting_def[0], setting_def[1], setting_def[3],
                                                             saved_data.get(setting_def[0], None))
            self.settings[new_setting.key] = new_setting
        self.loaded_settings = True

    def __getitem__(self, item):
        if not self.loaded_settings:
            self.load_settings()
        return self.settings[item].value

    def load_cmdsets(self):
        for cmdset in self.cmdsets:
            self.owner.cmdset.add(cmdset)

    def load(self):
        pass

    def load_final(self):
        pass

    def set_db(self, name, value):
        return self.owner.attributes.add(name, value, category=self.key)

    def get_db(self, name, default=None):
        return self.owner.attributes.get(name, category=self.key) or default

    def save_settings(self):
        save_data = dict()
        for setting in self.settings.values():
            data = setting.export()
            if len(data):
                save_data[setting.key] = data
        self.set_db('settings', save_data)

    def change_settings(self, session, key, value):
        setting = partial_match(key, self.settings.values())
        if not setting:
            raise AthException("Setting '%s' not found!" % key)
        old_value = setting.display()
        setting.set(value, str(value).split(','), session)
        self.save_settings()
        return setting, old_value

    def get_colors(self):
        pass

    def alert(self, text, system=None):
        if not system:
            system = self.system_name
        if not self.owner.sessions.all():
            return
        colors = self.get_colors()
        msg_edge = colors['msg_edge_color'].value
        msg_name = colors['msg_name_color'].value
        message = '|%s-=<|n|%s%s|n|%s>=-|n %s' % (msg_edge, msg_name, system.upper(), msg_edge, text)
        self.owner.msg(message)


class CharacterBaseHelper(BaseHelper):
    mode = 'character'

    def get_colors(self):
        return self.owner.account.ath['color'].get_settings()

    def at_init(self):
        pass

    def at_object_creation(self):
        pass

    def at_post_unpuppet(self, account, session, **kwargs):
        pass

    def at_true_logout(self, account, session, **kwargs):
        pass

    def at_true_login(self, **kwargs):
        pass

    def at_post_puppet(self, **kwargs):
        pass


class AccountBaseHelper(BaseHelper):

    def get_colors(self):
        return self.owner.ath['color'].get_settings()

    def at_account_creation(self):
        pass

    def at_post_login(self, session, **kwargs):
        pass

    def at_true_login(self, session, **kwargs):
        pass

    def at_failed_login(self, session, **kwargs):
        pass

    def at_init(self):
        pass

    def at_disconnect(self, reason, **kwargs):
        pass

    def at_true_logout(self, **kwargs):
        pass

    def render_login(self, session, viewer):
        pass


class ScriptBaseHelper(BaseHelper):
    pass


class SessionBaseHelper(BaseHelper):

    def at_sync(self):
        pass

    def at_login(self, account, **kwargs):
        pass

    def at_disconnect(self, reason, **kwargs):
        pass

    def load_file(self, file):
        pass

    def save_file(self, file):
        pass

    def save(self):
        pass

    def set_db(self, name, value):
        return self.owner.nattributes.add(name, value)

    def get_db(self, name, default=None):
        return self.owner.nattributes.get(name, default=default)

    def alert(self, text, system=None):
        self.owner.msg(text)


class RenderBaseHelper(BaseHelper):

    @property
    def settings_data(self):
        styles = self.base.styles
        output = list()
        for k, v in styles.items():
            output.append((k, v[0], v[1], v[2]))
        return tuple(output)

    def width(self, session):
        return session.protocol_flags['SCREENWIDTH'][0]

    def create_table(self, session, columns, border='cols', header=True, width=None, **kwargs):
        border_color = self['border_color']
        column_color = self['table_column_header_text_color']

        colornames = ['|%s%s|n' % (column_color, col[0]) for col in columns]
        header_line_char = ANSIString('|%s-|n' % border_color)
        corner_char = ANSIString('|%s+|n' % border_color)
        border_left_char = ANSIString('|%s|||n' % border_color)
        border_right_char = ANSIString('|%s|||n' % border_color)
        border_bottom_char = ANSIString('|%s-|n' % border_color)
        border_top_char = ANSIString('|%s-|n' % border_color)

        if not width:
            width = self.width(session)

        table = EvTable(*colornames, border=border, pad_width=0, valign='t', header_line_char=header_line_char,
                                corner_char=corner_char, border_left_char=border_left_char,
                                border_right_char=border_right_char, border_bottom_char=border_bottom_char,
                                border_top_char=border_top_char, header=header, width=width, maxwidth=width)

        # Tables always have the borders on each side, so let's subtract two characters.
        for count, column in enumerate(columns):
            if column[1]:
                table.reformat_column(count, width=column[1], align=column[2])
            else:
                table.reformat_column(count, align=column[2])
        return table

    def render_header(self, session, header_text=None, fill_character=None, edge_character=None,
                      mode='header', color_header=True):
        colors = dict()
        colors['border'] = self['%s_fill_color' % mode]
        colors['headertext'] = self['%s_text_color' % mode]
        colors['headerstar'] = self['%s_star_color' % mode]

        width = self.width(session)
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

        fill_character = self['%s_fill' % mode]

        remain_fill = width - len(center_string)
        if remain_fill % 2 == 0:
            right_width = remain_fill / 2
            left_width = remain_fill / 2
        else:
            right_width = math.floor(remain_fill / 2)
            left_width = math.ceil(remain_fill / 2) + 1

        right_fill = ANSIString('|n|%s%s|n' % (colors['border'], fill_character * int(right_width)))
        left_fill = ANSIString('|n|%s%s|n' % (colors['border'], fill_character * int(left_width)))

        if edge_character:
            edge_fill = ANSIString('|n|%s%s|n' % (colors['border'], edge_character))
            main_string = ANSIString(center_string)
            final_send = ANSIString(edge_fill) + left_fill + main_string + right_fill + ANSIString(edge_fill)
        else:
            final_send = left_fill + ANSIString(center_string) + right_fill
        return final_send

    def header(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'header'
        return self.render_header(*args, **kwargs)

    def subheader(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'subheader'
        return self.render_header(*args, **kwargs)

    def separator(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'separator'
        return self.render_header(*args, **kwargs)

    def footer(self, *args, **kwargs):
        if 'mode' not in kwargs:
            kwargs['mode'] = 'footer'
        return self.render_header(*args, **kwargs)

    def columns(self, session, column_text):
        return ANSIString('|%s%s|n' % (self['table_column_header_text_color'], column_text))

    def local_time(self, date=None, time_format=None, tz=None):
        """
        Displays a DateTime in a localized timezone to the account.

        :param date: A datetime object. Will be utcnow() if not provided.
        :param format: a strftime formatter.
        :return: Time as String
        """
        if not time_format:
            time_format = '%b %d %I:%M%p %Z'
        if not date:
            date = utcnow()
        if not tz:
            tz = self.base['core'].timezone
        results = date.astimezone(tz)
        return time.strftime(time_format)