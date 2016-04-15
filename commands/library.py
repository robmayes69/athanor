from __future__ import unicode_literals

import re, datetime
from django.conf import settings
from django.utils.timezone import utc
import evennia
from evennia.utils.ansi import ANSIString, ANSI_PARSER
from evennia.utils import evtable, create

def make_table(*args, **kwargs):
    border_color = None
    column_color = None
    if 'border' in kwargs:
        border = kwargs['border']
    else:
        border = "cols"
    if 'header' in kwargs:
        header = kwargs['header']
    else:
        header = True
    if 'viewer' in kwargs:
        viewer = kwargs['viewer']
        try:
            border_color = viewer.settings.get('border_color')
            column_color = viewer.settings.get('columnname_color')
        except AttributeError:
            border_color = 'M'
            column_color = 'G'
    else:
        border_color = 'M'
        column_color = 'G'
    if 'border_color' in kwargs:
        border_color = kwargs['border_color']
    if 'column_color' in kwargs:
        column_color = kwargs['column_color']

    args = ['{%s%s{n' % (column_color, name) for name in args]
    header_line_char = ANSIString('{%s-{n' % border_color)
    corner_char = ANSIString('{%s+{n' % border_color)
    border_left_char = ANSIString('{%s|{n' % border_color)
    border_right_char = ANSIString('{%s|{n' % border_color)
    border_bottom_char = ANSIString('{%s-{n' % border_color)
    border_top_char = ANSIString('{%s-{n' % border_color)

    table = evtable.EvTable(*args, border=border, pad_width=0, valign='t', header_line_char=header_line_char,
                            corner_char=corner_char, border_left_char=border_left_char,
                            border_right_char=border_right_char, border_bottom_char=border_bottom_char,
                            border_top_char=border_top_char, header=header)

    if "width" in kwargs:
        for count, width in enumerate(kwargs['width']):
            table.reformat_column(count, width=width)
    return table


def make_column_table(*args, **kwargs):
    if 'border' in kwargs:
        border = kwargs['border']
    else:
        border = "cols"
    if 'header' in kwargs:
        header = kwargs['header']
    else:
        header = False

    table = evtable.EvTable(*args, border=border,pad_width=0, valign='t', header_line_char=ANSIString('{M-|n'),
                            corner_char=ANSIString('{M+|n'), border_left_char=ANSIString('{M||n'),
                            border_right_char=ANSIString('{M||n'), border_bottom_char=ANSIString('{M-|n'),
                            border_top_char=ANSIString('{M-|n'), header=header)
    return table

def start_menu(*args, **kwargs):
    from commands.menu import AthanorMenu
    if 'node_formatter' not in kwargs:
        kwargs['node_formatter'] = node_formatter
    if 'nodetext_formatter' not in kwargs:
        kwargs['nodetext_formatter'] = nodetext_formatter
    if 'options_formatter' not in kwargs:
        kwargs['options_formatter'] = options_formatter

    return AthanorMenu(*args, **kwargs)

def node_formatter(main_text, option_text, viewer):
    return "\n".join(line for line in [main_text, option_text])


def options_formatter(options, viewer):
    message = list()
    message.append(header('Options', viewer=viewer))
    options_table = make_table('Option', 'Description', width=[20, 58])
    for num, option in enumerate(options):
        options_table.add_row(option[0], option[1])
    message.append(options_table)
    message.append(header())
    return "\n".join(unicode(line) for line in message)


def nodetext_formatter(text, options, viewer):
    message = list()
    #message.append(header(viewer=viewer))
    message.append(text)
    return "\n".join(unicode(line) for line in message)


def connected_sessions():
    """
    Simple shortcut to retrieving all connected sessions.

    Returns:
        list
    """
    return evennia.SESSION_HANDLER.values()


def connected_players(viewer=None):
    """
    Uses the current online sessions to derive a list of connected players.

    Returns:
        list
    """
    from typeclasses.players import Player
    return sorted([player for player in evennia.SESSION_HANDLER.all_connected_players()
            if player.is_typeclass(Player, exact=False)], key=lambda play: play.key)

def connected_characters(viewer=None):
    """
    Uses the current online sessions to derive a list of connected characters.

    Returns:
        list
    """
    from typeclasses.characters import Character
    characters = [session.get_puppet() for session in connected_sessions() if session.get_puppet()]
    characters = [char for char in characters if char.is_typeclass(Character, exact=False)]
    character_list = sorted(list(set(characters)), key=lambda char: char.key)
    if viewer:
        return [char for char in character_list if viewer.can_see(char)]
    return character_list


def utcnow():
    """
    Simply returns a datetime of the current instant in UTC.

    Returns:
        datetime
    """
    return datetime.datetime.utcnow().replace(tzinfo=utc)


def duration_from_string(time_string):
    """
    Take a string and derive a datetime timedelta from it.

    Args:
        time_string (string): This is a string from user-input. The intended format is, for example: "5d 2w 90s" for
                            'five days, two weeks, and ninety seconds.' Invalid sections are ignored.

    Returns:
        timedelta

    """
    time_string = time_string.split(" ")
    seconds = 0
    minutes = 0
    hours = 0
    days = 0
    weeks = 0

    for interval in time_string:
        if re.match(r'^[\d]+s$', interval.lower()):
            seconds =+ int(interval.lower().rstrip("s"))
        elif re.match(r'^[\d]+m$', interval):
            minutes =+ int(interval.lower().rstrip("m"))
        elif re.match(r'^[\d]+h$', interval):
            hours =+ int(interval.lower().rstrip("h"))
        elif re.match(r'^[\d]+d$', interval):
            days =+ int(interval.lower().rstrip("d"))
        elif re.match(r'^[\d]+w$', interval):
            weeks =+ int(interval.lower().rstrip("w"))
        elif re.match(r'^[\d]+y$', interval):
            days =+ int(interval.lower().rstrip("y")) * 365
        else:
            raise ValueError("Could not convert section '%s' to a time duration." % interval)

    return datetime.timedelta(days, seconds, 0, 0, minutes, hours, weeks)


def mxp_send(text="", command="", hints=""):
    if text:
        return ANSIString("{lc%s{lt%s{le" % (command, text))
    else:
        return ANSIString("{lc%s{lt%s{le" % (command, command))


def partial_match(match_text, candidates):
    candidate_list = sorted(candidates, key=lambda item: len(str(item)))
    for candidate in candidate_list:
        if match_text.lower() == str(candidate).lower():
            return candidate
        if str(candidate).lower().startswith(match_text.lower()):
            return candidate


MAIN_COLOR_KEYS = ['borders', 'alerts', 'rooms']
MAIN_COLOR_OPTIONS = {'borders': ['border', 'bordertext', 'borderdot'],
                      'alerts': ['border', 'roomdot', 'text', 'error'],
                      'rooms': ['players', 'exitnames', 'exitalias', 'border', 'bordertext', 'borderdot']}
MAIN_COLOR_DEFAULTS = {'borders': {'border': 'M', 'bordertext': 'w', 'borderdot': 'm',},
                       'alerts': {'text': 'w', 'border': 'M', 'roomdot': 'm', 'error': 'r'},
                       'rooms': {'players': 'n', 'exitnames': 'n', 'exitalias': 'x', 'border': 'M', 'bordertext': 'w', 'borderdot': 'm'},}


def header(header_text=None, width=78, width_mode='fixed', fill_character=None, edge_character=None,
           edges=False, viewer=None, mode='header', color_header=True):
    colors = {}
    if viewer:
        try:
            colors['border'] = viewer.settings.get('border_color')
            colors['headertext'] = viewer.settings.get('headertext_color')
            colors['headerstar'] = viewer.settings.get('headerstar_color')
        except AttributeError:
            colors['border'] = MAIN_COLOR_DEFAULTS['borders']['border']
            colors['headertext'] = MAIN_COLOR_DEFAULTS['borders']['bordertext']
            colors['headerstar'] = MAIN_COLOR_DEFAULTS['borders']['borderdot']
    else:
        colors['border'] = MAIN_COLOR_DEFAULTS['borders']['border']
        colors['headertext'] = MAIN_COLOR_DEFAULTS['borders']['bordertext']
        colors['headerstar'] = MAIN_COLOR_DEFAULTS['borders']['borderdot']

    if width_mode == 'variable' and viewer:
        width = viewer.screen_width
    if edges:
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

    if not fill_character and mode == 'header':
        fill_character = '='
    elif not fill_character and mode == 'subheader':
        fill_character = '='
    elif not fill_character:
        fill_character = '-'
    fill = ANSIString('|n|%s%s|n' % (colors['border'], fill_character))

    if edges:
        if not edge_character:
            edge_character = '='
        edge_fill = ANSIString('|n|%s%s|n' % (colors['border'], edge_character))
        main_string = ANSIString(center_string).center(width, fill)
        return ANSIString(edge_fill) + ANSIString(main_string) + ANSIString(edge_fill)
    else:
        return ANSIString(center_string).center(width, fill)


def subheader(*args, **kwargs):
    if 'mode' not in kwargs:
        kwargs['mode'] = 'subheader'
    return header(*args, **kwargs)


def separator(*args, **kwargs):
    if 'mode' not in kwargs:
        kwargs['mode'] = 'separator'
    return header(*args, **kwargs)




class Speech(object):
    """
    This class is similar to the Evennia Msg in that it represents an entity speaking.
    It is meant to render speech from a player or character. The output replicates MUSH-style
    speech from varying input. Intended output:

    If input = ':blah.', output = 'Character blah.'
    If input = ';blah.', output = 'Characterblah.'
    If input = |blah', output = 'blah'
    If input = 'blah.', output = 'Character says, "Blah,"'

    """

    def __init__(self, speaker, speech_text, alternate_name=None, title=None, mode='ooc'):
        from typeclasses.characters import Character
        self.character_dict = dict()
        self.character_id = dict()
        for char in Character.objects.filter_family():
            self.character_dict[char.key.upper()] = char.id
            self.character_id[char.id] = char

        def markup_names(match, char_dict=self.character_dict):
            found = match.group('found')
            if found[0].isupper():
                return '^^^%s:%s^^^' % (char_dict[found.upper()], found)
            return found

        self.speaker = speaker
        if alternate_name:
            self.display_name = alternate_name
            self.markup_name = alternate_name
        else:
            self.display_name = str(speaker)
            self.markup_name = '^^^%s:%s^^^' % (speaker.id, speaker.key)
        self.title = title
        self.mode = mode

        speech_text = ANSIString(speech_text)

        if speech_text[:1] == ':':
            special_format = 1
            speech_string = speech_text[1:]
        elif speech_text[:1] == ';':
            special_format = 2
            speech_string = speech_text[1:]
        elif speech_text[:1] == '|':
            special_format = 3
            speech_string = speech_text[1:]
        elif speech_text[:1] in ['"', "'"]:
            special_format = 0
            speech_string = speech_text[1:]
        else:
            special_format = 0
            speech_string = speech_text

        self.special_format = special_format
        self.speech_string = ANSIString(speech_string)

        escape_names = [re.escape(name) for name in self.character_dict.keys()]
        all_names = '|'.join(escape_names)
        self.markup_string = re.sub(r"(?i)\b(?P<found>%s)\b" % all_names, markup_names, self.speech_string)

    def __str__(self):
        str(unicode(self))

    def __unicode__(self):
        return unicode(self.demarkup())

    def monitor_display(self, viewer=None):
        if not viewer:
            return self.demarkup()
        if not self.codename:
            return self.render(viewer)
        return_string = None
        if self.special_format == 0:
            return_string = '(%s)%s says, "%s"' % (self.markup_name, self.codename, self.markup_string)
        elif self.special_format == 1:
            return_string = '(%s)%s %s' % (self.markup_name, self.codename, self.markup_string)
        elif self.special_format == 2:
            return_string = '(%s)%s%s' % (self.markup_name, self.codename, self.markup_string)
        elif self.special_format == 3:
            return_string = '(%s)%s' % (self.markup_name, self.markup_string)
        if self.title:
            return_string = '%s %s' % (self.title, return_string)

        return self.colorize(return_string, viewer)

    def render(self, viewer=None):
        if not viewer:
            return ANSIString(self.demarkup())
        return_string = None
        if self.special_format == 0:
            return_string = '%s says, "%s|n"' % (self.markup_name, self.markup_string)
        elif self.special_format == 1:
            return_string = '%s %s' % (self.markup_name, self.markup_string)
        elif self.special_format == 2:
            return_string = '%s%s' % (self.markup_name, self.markup_string)
        elif self.special_format == 3:
            return_string = self.markup_string
        if self.title:
            return_string = '%s %s' % (self.title, return_string)

        return self.colorize(return_string, viewer)

    def demarkup(self):
        return_string = None
        if self.special_format == 0:
            return_string = '%s says, "%s|n"' % (self.display_name, self.speech_string)
        elif self.special_format == 1:
            return_string = '%s %s' % (self.display_name, self.speech_string)
        elif self.special_format == 2:
            return_string = '%s%s' % (self.display_name, self.speech_string)
        elif self.special_format == 3:
            return_string = self.speech_string
        if self.title:
            return_string = '%s %s' % (self.title, return_string)
        return ANSIString(return_string)

    def colorize(self, message, viewer):
        quotes = 'quotes_%s' % self.mode
        speech = 'speech_%s' % self.mode
        quote_color = viewer.settings.get(quotes)
        speech_color = viewer.settings.get(speech)
        def color_speech(found, viewer=viewer):
            return '|%s"|n|%s%s|n|%s"|n' % (quote_color, speech_color, found.group('found'), quote_color)

        def color_names(found, viewer=viewer):
            try:
                id = int(found.group('id'))
            except:
                return found.group('name')
            if id in self.character_id:
                color = viewer.settings.get_color_name(self.character_id[id])
                return '|n|%s%s|n' % (color, found.group('name'))
            return found.group('name')

        colorized_string = re.sub(r'(?s)"(?P<found>.*?)"', color_speech, message)
        names_string = re.sub(r'\^\^\^(?P<id>\d+)\:(?P<name>[^^]+)\^\^\^', color_names, colorized_string)
        return names_string

def tabular_table(word_list=[], field_width=26, line_length=78, output_separator=" ", truncate_elements=True):
    """
    This function returns a tabulated string composed of a basic list of words.
    """
    elements = [ANSIString(entry) for entry in word_list]
    if truncate_elements:
        elements = [entry[:field_width] for entry in elements]
    elements = [entry.ljust(field_width) for entry in elements]
    separator_length = len(output_separator)
    per_line = line_length / (field_width + separator_length)
    result_string = ANSIString("")
    count = 0
    total = len(elements)
    for num, element in enumerate(elements):
        count += 1
        if count == 1:
            result_string += element
        elif count == per_line:
            result_string += output_separator
            result_string += element
            if not num+1 == total:
                result_string += '\n'
            count = 0
        elif count > 1:
            result_string += output_separator
            result_string += element
    return result_string


def sanitize_string(input=None, length=None, strip_ansi=False, strip_mxp=True, strip_newlines=True, strip_indents=True):
    if not input:
        return ''
    input = input.strip()
    if strip_mxp:
        input = ANSI_PARSER.strip_mxp(input)
    if strip_ansi:
        input = ANSIString(input).clean()
        input = input
    if strip_newlines:
        for bad_char in ['\n', '%r', '%R', '|/']:
            input = input.replace(bad_char, '')
    if strip_indents:
        for bad_char in ['\t', '%t', '%T', '|-']:
            input = input.replace(bad_char, '')
    if length:
        input = input[:length]
    return input


def dramatic_capitalize(capitalize_string=''):
    capitalize_string = re.sub(r"(?i)(?:^|(?<=[_\/\-\|\s()\+]))(?P<name1>[a-z]+)",
                               lambda find: find.group('name1').capitalize(), capitalize_string.lower())
    capitalize_string = re.sub(r"(?i)\b(of|the|a|and|in)\b", lambda find: find.group(1).lower(), capitalize_string)
    capitalize_string = re.sub(r"(?i)(^|(?<=[(\|\/]))(of|the|a|and|in)",
                               lambda find: find.group(1) + find.group(2).capitalize(), capitalize_string)
    return capitalize_string

def penn_substitutions(input=None):
    if not input:
        return ''
    for bad_char in ['%r', '%R']:
        input = input.replace(bad_char, '|/')
    for bad_char in ['%t', '%T']:
        input = input.replace(bad_char, '|-')
    return input