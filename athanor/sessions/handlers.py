import math
from evennia.utils.ansi import ANSIString
from evennia.utils import evtable
import athanor
from athanor.base.handlers import SessionBaseHandler


class SessionCoreHandler(SessionBaseHandler):
    key = 'core'
    style = 'fallback'
    system_name = 'SYSTEM'
    operations = ('create_account', 'create_character', 'set_account_disabled', 'set_character_disabled',
                  'set_account_banned', 'set_character_banned', 'set_character_shelved', 'login_account',
                  'puppet_character')
    cmdsets = ('athanor.sessions.unlogged.UnloggedCmdSet',)

    def at_sync(self):
        if not self.owner.logged_in:
            for cmdset in self.cmdsets:
                self.owner.cmdset.add(cmdset)

    def at_login(self, account, **kwargs):
        for cmdset in self.cmdsets:
            self.owner.cmdset.remove(cmdset)

    def is_builder(self):
        if not self.owner.account:
            return False
        return self.owner.account.ath['core'].is_builder()

    def is_admin(self):
        if not self.owner.account:
            return False
        return self.owner.account.ath['core'].is_admin()

    def is_developer(self):
        if not self.owner.account:
            return False
        return self.owner.account.ath['core'].is_developer()

    def is_superuser(self):
        if not self.owner.account:
            return False
        return self.owner.account.is_superuser

    def permission_rank(self):
        if not self.owner.account:
            return 0
        return self.owner.account.ath['core'].permission_rank()

    def can_modify(self, target):
        if not self.permission_rank() > 2:
            return False
        return self.permission_rank() > target.ath['core'].permission_rank()


class SessionRendererHandler(SessionBaseHandler):
    key = 'render'

    def width(self):
        return self.owner.protocol_flags['SCREENWIDTH'][0]

    def load_settings(self):
        for k, v in athanor.LOADER.styles.items():
            try:
                new_setting = athanor.LOADER.settings[v[0]](self, k, v[1], v[2], None)
                self.settings[new_setting.key] = new_setting
            except Exception as e:
                print("Cannot load setting: %s" % e)
                pass

    def get_settings(self):
        if hasattr(self.owner, 'account'):
            return self.owner.account.ath['color'].get_settings()
        if not self.loaded_settings:
            self.load_settings()
        return self.settings

    def table(self, columns, border='cols', header=True, width=None, **kwargs):
        colors = self.get_settings()
        border_color = colors['border_color'].value
        column_color = colors['table_column_header_text_color'].value

        colornames = ['|%s%s|n' % (column_color, col[0]) for col in columns]
        header_line_char = ANSIString('|%s-|n' % border_color)
        corner_char = ANSIString('|%s+|n' % border_color)
        border_left_char = ANSIString('|%s|||n' % border_color)
        border_right_char = ANSIString('|%s|||n' % border_color)
        border_bottom_char = ANSIString('|%s-|n' % border_color)
        border_top_char = ANSIString('|%s-|n' % border_color)

        if not width:
            width = self.width()

        table = evtable.EvTable(*colornames, border=border, pad_width=0, valign='t', header_line_char=header_line_char,
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

    def header(self, header_text=None, fill_character=None, edge_character=None, mode='header', color_header=True):
        styles = self.get_settings()
        colors = dict()
        colors['border'] = styles['%s_fill_color' % mode].value
        colors['headertext'] = styles['%s_text_color' % mode].value
        colors['headerstar'] = styles['%s_star_color' % mode].value

        width = self.width()
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

        fill_character = styles['%s_fill' % mode].value

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
