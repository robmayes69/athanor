
import re
from evennia.utils.ansi import ANSIString, ANSI_PARSER
from athanor import AthException, SYSTEMS

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
    speech_dict = {':': 1, ';': 2, '|': 3, '"': 0, "'": 0}

    def __init__(self, speaker=None, speech_text=None, alternate_name=None, title=None, mode='ooc', system_name=None, targets=None, rendered_text=None):
        self.name_dict = SYSTEMS['character'].name_map
        self.targets = ['$charactername(%s,%s)' % (char.id, char.key) for char in targets]
        self.mode = mode
        self.title = title
        self.speaker = speaker

        if alternate_name:
            self.alternate_name = alternate_name
            self.display_name = alternate_name
            self.markup_name = alternate_name
        else:
            self.display_name = str(speaker)
            self.alternate_name = False
            self.markup_name = '$charactername(%s,%s)' % (speaker.id, speaker.key)

        speech_text = ANSIString(speech_text)
        speech_first = speech_text[:1]
        if speech_first in self.speech_dict:
            special_format = self.speech_dict[speech_first]
            speech_string = speech_text[1:]
        else:
            special_format = 0
            speech_string = speech_text

        self.special_format = special_format
        self.speech_string = ANSIString(speech_string)

        if rendered_text:
            self.markup_string = rendered_text
        else:
            escape_names = [re.escape(name) for name in self.name_dict.keys()]
            all_names = '|'.join(escape_names)
            self.markup_string = re.sub(r"(?i)\b(?P<found>%s)\b" % all_names, self.markup_names, self.speech_string)

    def markup_names(self, match):
        found = match.group('found')
        return '$charactername(%s,%s)' % (self.name_dict[found.upper()], found)

    def __str__(self):
        str(unicode(self))

    def __unicode__(self):
        return unicode(self.demarkup())

    def monitor_display(self, viewer=None):
        if not viewer:
            return self.demarkup()
        if not self.alternate_name:
            return self.render(viewer)
        return_string = None
        if self.special_format == 0:
            return_string = '(%s)%s says, "%s"' % (self.markup_name, self.alternate_name, self.markup_string)
        elif self.special_format == 1:
            return_string = '(%s)%s %s' % (self.markup_name, self.alternate_name, self.markup_string)
        elif self.special_format == 2:
            return_string = '(%s)%s%s' % (self.markup_name, self.alternate_name, self.markup_string)
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

        colorized_string = re.sub(r'(?s)"(?P<found>.*?)"', color_speech, message)
        return colorized_string