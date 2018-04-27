from __future__ import unicode_literals
import re
from evennia.utils.ansi import ANSIString, ANSI_PARSER

def tabular_table(word_list=None, field_width=26, line_length=78, output_separator=" ", truncate_elements=True):
    """
    This function returns a tabulated string composed of a basic list of words.
    """
    if not word_list:
        word_list = list()
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

def sanitize_string(text=None, length=None, strip_ansi=False, strip_mxp=True, strip_newlines=True, strip_indents=True):
    if not text:
        return ''
    text = text.strip()
    if strip_mxp:
        text = ANSI_PARSER.strip_mxp(text)
    if strip_ansi:
        text = ANSIString(text).clean()
    if strip_newlines:
        for bad_char in ['\n', '%r', '%R', '|/']:
            text = text.replace(bad_char, '')
    if strip_indents:
        for bad_char in ['\t', '%t', '%T', '|-']:
            text = text.replace(bad_char, '')
    if length:
        text = text[:length]
    return text

def normal_string(text=None):
    return sanitize_string(text, strip_ansi=True)

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

SYSTEM_CHARACTERS = ('/','|','=',',')

def sanitize_name(name, system_name):
    name = sanitize_string(name)
    if not name:
        raise AthException("%s names must not be empty!" % system_name)
    for char in SYSTEM_CHARACTERS:
        if char in name:
            raise AthException("%s is not allowed in %s names!" % (char, system_name))
    return name

def sanitize_board_name(name):
    return sanitize_name(name, 'Board')

def sanitize_group_name(name):
    return sanitize_name(name, 'Group')

def partial_match(match_text, candidates):
    candidate_list = sorted(candidates, key=lambda item: len(str(item)))
    for candidate in candidate_list:
        if match_text.lower() == str(candidate).lower():
            return candidate
        if str(candidate).lower().startswith(match_text.lower()):
            return candidate


def mxp(text="", command="", hints=""):
    if text:
        return ANSIString("|lc%s|lt%s|le" % (command, text))
    else:
        return ANSIString("|lc%s|lt%s|le" % (command, command))

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

    def __init__(self, speaker, speech_text, alternate_name=None, title=None, mode='ooc', char_dict=None,
                 name_dict=None, targets=None):
        self.char_dict = char_dict
        self.name_dict = name_dict
        self.upper_dict = dict()
        self.targets = ['^^^%s:%s^^^' % (char.id, char.key) for char in targets]
        for key in name_dict.keys():
            self.upper_dict[name_dict[key].upper()] = key

        def markup_names(match):
            found = match.group('found')
            return '^^^%s:%s^^^' % (self.upper_dict[found.upper()], found)

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

        escape_names = [re.escape(name) for name in name_dict.values()]
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
        if self.mode == 'page' and len(self.targets) > 1:
            pref = '(To %s)' % (', '.join(self.targets))
            return_string = '%s %s' % (pref, return_string)

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
        quote_color = viewer.player_config[quotes]
        speech_color = viewer.player_config[speech]
        def color_speech(found, viewer=viewer):
            return '|%s"|n|%s%s|n|%s"|n' % (quote_color, speech_color, found.group('found'), quote_color)

        def color_names(found, viewer=viewer):
            try:
                id = int(found.group('id'))
            except:
                return found.group('name')
            if id in self.name_dict:
                color = viewer.player.colors.characters.get(self.char_dict[id], None)
                if not color:
                    return found.group('name')
                return '|n|%s%s|n' % (color, found.group('name'))
            return found.group('name')

        colorized_string = re.sub(r'(?s)"(?P<found>.*?)"', color_speech, message)
        names_string = re.sub(r'\^\^\^(?P<id>\d+)\:(?P<name>[^^]+)\^\^\^', color_names, colorized_string)
        return names_string