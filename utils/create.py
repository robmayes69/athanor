from __future__ import unicode_literals

from django.conf import settings
from evennia.utils.create import create_channel, create_player, create_object
from athanor.core.config import GLOBAL_SETTINGS, CharacterSetting

class CharacterList(object):
    def __init__(self, id):
        from athanor.classes.characters import Character
        self.id = id
        self.char_dict = {char.id: char.key for char in
                          Character.objects.filter_family(character_settings__enabled=True)}

    def update(self, character):
        self.char_dict[character.id] = character.key

    def values(self):
        return self.char_dict.values()

    def keys(self):
        return self.char_dict.keys()

    def upper(self):
        return [name.upper() for name in self.values()]


CHARACTER_MANAGER = CharacterList(0)


def player(key, password, email=None):
    return create_player(key, email, password)

def character(key, player):
    typeclass = settings.BASE_CHARACTER_TYPECLASS
    home = GLOBAL_SETTINGS['character_home']
    if key.upper() in CHARACTER_MANAGER.upper():
        raise ValueError("That character name is already in use!")
    char = create_object(typeclass=typeclass, key=key, location=home, home=home)
    player.account.bind_character(char)
    CHARACTER_MANAGER.update(char)
    return char