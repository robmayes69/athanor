
from evennia import ObjectDB
from django.conf import settings
from evennia.utils.create import create_channel, create_account, create_object
from athanor.utils.text import Speech, sanitize_string


def account(key, password, email=None):
    return create_account(key, email, password)


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
        return [key.key.upper() for key in self.values()]

    def __getitem__(self, item):
        if not self.loaded:
            self.load()
        return self.name_dict[item]

    def create(self, speaker, speech_text, alternate_name=None, title=None, mode='ooc', targets=None):
        if not self.loaded:
            self.load()
        return Speech(speaker, speech_text, alternate_name, title, mode, char_dict=self.char_dict,
                      name_dict=self.name_dict, targets=targets)

#SPEECH_FACTORY = SpeechFactory()

def make_speech(speaker, speech_text, alternate_name=None, title=None, mode='ooc', targets=None):
    pass #return SPEECH_FACTORY.create(speaker, speech_text, alternate_name, title, mode, targets)

def character(key, account):
    typeclass = settings.BASE_CHARACTER_TYPECLASS
    char = create_object(typeclass=typeclass, key=key)
    account.ath['character'].add(char)
    #SPEECH_FACTORY.update(char)
    return char
