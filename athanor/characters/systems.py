from django.conf import settings
from evennia import create_object
from athanor import AthException
from athanor.base.systems import AthanorSystem


class CharacterSystem(AthanorSystem):
    key = 'character'
    system_name = 'CHARACTER'
    load_order = -998
    settings_data = (
        ('rename_self', "Can players rename their own characters?", 'boolean', True),
    )

    def load(self):
        from athanor.characters.classes import Character
        results = Character.objects.filter_family().values_list('id', 'db_key')
        self.name_map = {q[1].upper(): q[0] for q in results}

    def create(self, session, account, name):
        account = self.valid['account'](session, account)
        name = self.valid['character_name'](session, name)
        typeclass = settings.BASE_CHARACTER_TYPECLASS
        new_char = create_object(typeclass=typeclass, key=name)
        account.ath['character'].add(new_char)
        self.name_map[new_char.key.upper()] = new_char.id
        return new_char

    def rename(self, session, character, new_name):
        character = self.valid['character'](session, character)
        new_name = self.valid['character_name'](session, character, new_name)
        old_name = character.key
        if character.key.upper() in self.name_map:
            del self.name_map[old_name.upper()]
        character.key = new_name
        self.name_map[character.key.upper()] = character.id

    def reassign(self, session, character, account):
        pass

    def get(self, session, character):
        character = self.valid['character'](session, character)
        return character

    def disable(self, session, character):
        pass

    def enable(self, session, character):
        pass

    def ban(self, session, character, duration):
        pass

    def unban(self, session, character):
        pass