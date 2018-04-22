import importlib, math
from django.conf import settings

from evennia.utils.ansi import ANSIString
from evennia.utils import evtable
from athanor.styles.game_styles import ATHANOR_STYLES
from athanor.styles.athanor_styles import FALLBACK


class __BaseTypeStyle(object):
    """
    The base used for the Athanor Handlers that are loaded onto all Athanor Accounts and Characters.

    Not meant to be used directly.
    """
    mode = None
    fallback = FALLBACK

    def get_styles(self):
        pass


    def __init__(self, owner):
        """

        :param owner: An instance of a TypeClass'd object.
        """
        self.owner = owner
        self.attributes = owner.attributes
        self.styles = dict()
        self.get_styles()

        # Call an extensible Load function for simplicity if need be.
        self.load()

    def load(self):
        pass

    def __getitem__(self, item):
        if item in self.styles:
            return self.styles[item]

        # If it doesn't exist, then we'll load it here.
        try:
            new_item = self.styles_dict[item](self)
            self.styles[item] = new_item
            return new_item
        except:
            return self.fallback


class CharacterTypeStyle(__BaseTypeStyle):
    mode = 'character'

    def get_styles(self):
        self.styles_list = list()
        for style in settings.ATHANOR_STYLES_CHARACTER:
            module = importlib.import_module(style)
            self.styles_list += module.ALL
        self.styles_dict = {style.key: style for style in self.styles_list}


class AccountTypeStyle(__BaseTypeStyle):
    mode = 'account'

    def get_styles(self):
        self.styles_list = list()
        for style in settings.ATHANOR_STYLES_ACCOUNT:
            module = importlib.import_module(style)
            self.styles_list += module.ALL
        self.styles_dict = {style.key: style for style in self.styles_list}


class ScriptTypeStyle(__BaseTypeStyle):
    mode = 'script'


class __BaseStyle(object):
    key = 'base'
    category = 'athanor_styles'
    style = 'fallback'
    system_name = 'SYSTEM'
    athanor_classes = ATHANOR_STYLES
    use_athanor_classes = True
    styles_classes = dict()

    def __init__(self, base):
        self.base = base
        self.owner = base.owner
        self.styles = dict()
        self.load()

    def load(self):
        load_data = self.base.attributes.get(key=self.key, default=dict(), category=self.category)
        if self.use_athanor_classes:
            for cls in self.athanor_classes:
                new_style = cls(self, load_data)
                self.styles[new_style.key] = new_style
        for cls in self.styles_classes:
            new_style = cls(self, load_data)
            self.styles[new_style.key] = new_style

    def __getitem__(self, item):
        return self.styles[item].value

    def save(self):
        save_data = {style.key: style.export() for style in self.styles.values() if style.loaded}
        self.base.attributes.add(key=self.key, value=save_data, category=self.category)


class CharacterStyle(__BaseStyle):
    pass


class AccountStyle(__BaseStyle):
    pass


class ScriptStyle(__BaseStyle):
    pass


class SessionRenderer(object):

    def __init__(self, owner):
        self.owner = owner
        self.fallback = FALLBACK

    def width(self):
        return 80

    def __getitem__(self, item):
        if self.owner.puppet:
            return self.owner.puppet.styles[item]
        if self.owner.account:
            return self.owner.account.styles[item]
        return self.fallback
    
    def table(self, columns, border='cols', header=True, style='fallback', width=None, **kwargs):
        colors = self[style]
        border_color = colors['border_color']
        column_color = colors['table_column_header_text_color']

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

    def header(self, header_text=None, fill_character=None, edge_character=None, mode='header', color_header=True,
               style='fallback'):
        styles = self[style]
        colors = {}
        colors['border'] = styles['%s_fill_color' % mode]
        colors['headertext'] = styles['%s_text_color' % mode]
        colors['headerstar'] = styles['%s_star_color' % mode]

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

        fill_character = styles['%s_fill' % mode]

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