from django.conf import settings
from evennia import create_object
from athanor.base.systems import AthanorSystem
from athanor.utils.online import characters as on_characters


class CharacterSystem(AthanorSystem):
    key = 'character'
    system_name = 'CHARACTER'
    load_order = -998
    settings_data = (
        ('rename_self', "Can players rename their own characters?", 'boolean', True),
    )
    run_interval = 60

    def load(self):
        from athanor.characters.classes import Character
        results = Character.objects.filter_family().values_list('id', 'db_key')
        self.ndb.name_map = {q[1].upper(): q[0] for q in results}
        self.ndb.online_characters = set(on_characters())

    def create(self, session, account, name):
        account = self.valid['account'](session, account)
        name = self.valid['character_name'](session, name)
        typeclass = settings.BASE_CHARACTER_TYPECLASS
        new_char = create_object(typeclass=typeclass, key=name)
        account.ath['character'].add(new_char)
        self.ndb.name_map[new_char.key.upper()] = new_char.id
        return new_char

    def rename(self, session, character, new_name):
        character = self.valid['character'](session, character)
        new_name = self.valid['character_name'](session, character, new_name)
        old_name = character.key
        if character.key.upper() in self.ndb.name_map:
            del self.ndb.name_map[old_name.upper()]
        character.key = new_name
        self.ndb.name_map[character.key.upper()] = character.id

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

    def render(self, input):
        return input

    def at_repeat(self):
        for acc in self.ndb.online_characters:
            acc.ath['core'].update_playtime(self.interval)

    def add_online(self, character):
        self.ndb.online_characters.add(character)

    def remove_online(self, character):
        self.ndb.online_characters.remove(character)
