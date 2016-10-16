from __future__ import unicode_literals

from evennia import ObjectDB
from django.conf import settings
from evennia.utils.create import create_channel, create_player, create_object
from athanor.utils.text import Speech, sanitize_string


def player(key, password, email=None):
    return create_player(key, email, password)

class SpeechFactory(object):

    def __init__(self):
        self.char_dict = dict()
        self.name_dict = dict()
        self.loaded = False

    def load(self):
        chars = ObjectDB.objects.filter(character_settings__enabled=True)
        chars = [char for char in chars if hasattr(char, 'ath_char')]
        self.char_dict = {char.id: char for char in chars}
        self.name_dict = {char.id: char.key for char in chars}
        self.loaded = True

    def update(self, character):
        if not self.loaded:
            self.load()
        self.char_dict[character.id] = character
        self.name_dict[character.id] = character.key

    def values(self):
        if not self.loaded:
            self.load()
        return self.char_dict.values()

    def keys(self):
        if not self.loaded:
            self.load()
        return self.char_dict.keys()

    def upper(self):
        if not self.loaded:
            self.load()
        return [key.upper() for key in self.keys()]

    def __getitem__(self, item):
        if not self.loaded:
            self.load()
        return self.name_dict[item]

    def create(self, speaker, speech_text, alternate_name=None, title=None, mode='ooc', targets=None):
        if not self.loaded:
            self.load()
        return Speech(speaker, speech_text, alternate_name, title, mode, char_dict=self.char_dict,
                      name_dict=self.name_dict, targets=targets)

SPEECH_FACTORY = SpeechFactory()

def make_speech(speaker, speech_text, alternate_name=None, title=None, mode='ooc', targets=None):
    return SPEECH_FACTORY.create(speaker, speech_text, alternate_name, title, mode, targets)

def character(key, player):
    from athanor.core.config import GLOBAL_SETTINGS
    key = sanitize_string(key, strip_ansi=True)
    typeclass = settings.BASE_CHARACTER_TYPECLASS
    home = GLOBAL_SETTINGS['character_home']
    if key.upper() in SPEECH_FACTORY.upper():
        raise ValueError("That character name is already in use!")
    char = create_object(typeclass=typeclass, key=key, location=home, home=home)
    player.account.bind_character(char)
    SPEECH_FACTORY.update(char)
    return char