from django.conf import settings
from evennia import create_object
from athanor import AthException
from athanor.base.systems import AthanorSystem
from athanor.utils.online import characters as on_characters
from athanor.utils.time import utcnow
from athanor.characters.classes import AthanorCharacter


class CharacterSystem(AthanorSystem):
    key = 'character'
    system_name = 'CHARACTER'
    load_order = -998
    settings_data = (
        ('rename_self', "Can players rename their own characters?", 'boolean', True),
    )
    run_interval = 60

    def search(self, session, find):
        if not find:
            raise AthException("Must enter search terms!")
        if find.lower() in ('self', 'me'):
            return session.get_puppet()
        if find.isdigit():
            results = AthanorCharacter.objects.filter_family(id=find).first()
        else:
            results = AthanorCharacter.objects.filter_family(db_key__iexact=find).first()
        if results:
            return results
        results = AthanorCharacter.objects.filter_family(db_key_istartswith=find).order_by('db_key')
        if results.count() > 1:
            raise AthException("Character Search Ambiguous. Matched: %s" % ', '.join(results))
        if not results:
            raise AthException("Character not found!")
        return results.first()

    def load(self):
        from athanor.characters.classes import AthanorCharacter
        results = AthanorCharacter.objects.filter_family().values_list('id', 'db_key')
        self.ndb.name_map = {q[1].upper(): q[0] for q in results}
        self.ndb.online_characters = set(on_characters())

    def create(self, session, account, name):
        account = self.valid['account'](session, account)
        if not (account == session.account or session.ath['core'].can_modify(account)):
            raise AthException("Permission denied!")
        name = self.valid['character_name'](session, name)
        typeclass = settings.BASE_CHARACTER_TYPECLASS
        new_char = create_object(typeclass=typeclass, key=name)
        account.ath['character'].add(new_char)
        self.ndb.name_map[new_char.key.upper()] = new_char.id
        account.ath['character'].alert("New Character Created: %s" % (new_char))
        self.alert("Created New Character: %s" % new_char, source=session)
        return new_char

    def rename(self, session, character, new_name):
        character = self.valid['character'](session, character)
        if not (session.ath['core'].can_modify(character) or (session.account == character.ath['core'].account and self['rename_self'])):
            raise AthException("Permission denied!")
        new_name = self.valid['character_name'](session, character, new_name)
        old_name = character.key
        if character.key.upper() in self.ndb.name_map:
            del self.ndb.name_map[old_name.upper()]
        character.key = new_name
        self.ndb.name_map[character.key.upper()] = character.id
        character.ath['core'].alert("You were renamed to: %s" % new_name)
        self.alert("Character '%s' renamed to: %s" % (old_name, new_name))
        return character, old_name, new_name

    def get(self, session, character):
        character = self.valid['character'](session, character)
        return character

    def disable(self, session, character):
        character = self.valid['character'](session, character)
        if session.get_puppet() == character:
            raise AthException("Cannot disable yourself!")
        if not session.account.ath['core'].can_modify(character):
            raise AthException("Permission denied.")
        character.ath['core'].alert("Your Character has been disabled!")
        character.ath['core'].disabled = True
        self.alert("Disabled Character '%s'" % character, source=session)
        return character

    def enable(self, session, character):
        character = self.valid['character'](session, character)
        if session.get_puppet() == character:
            raise AthException("Cannot disable yourself!")
        if not session.account.ath['core'].can_modify(character):
            raise AthException("Permission denied.")
        character.ath['core'].alert("Your Character has been Enabled!")
        character.ath['core'].disabled = False
        self.alert("Enabled Character '%s'" % character, source=session)
        return character

    def ban(self, session, character, duration):
        character = self.valid['character'](session, character)
        if session.get_puppet() == character:
            raise AthException("Cannot ban yourself!")
        if not session.account.ath['core'].can_modify(character):
            raise AthException("Permission denied.")
        duration = self.valid['duration'](session, duration)
        until = utcnow() + duration
        character.ath['core'].alert("Your Character has been banned for %s!" % duration)
        character.ath['core'].banned = until
        self.alert("Banned Character '%s' for %s - Until %s" % (character, duration, until), source=session)
        return character, duration, until

    def unban(self, session, character):
        character = self.valid['character'](session, character)
        if session.get_puppet() == character:
            raise AthException("Cannot ban yourself!")
        if not session.account.ath['core'].can_modify(character):
            raise AthException("Permission denied.")
        character.ath['core'].alert("Your Character has been un-banned!")
        character.ath['core'].banned = False
        self.alert("Un-Banned Character '%s'" % character, source=session)
        return character

    def render(self, input):
        return input

    def at_repeat(self):
        for acc in self.ndb.online_characters:
            acc.ath['core'].update_playtime(self.interval)

    def add_online(self, character):
        self.ndb.online_characters.add(character)

    def remove_online(self, character):
        self.ndb.online_characters.remove(character)

    def bind(self, session, character, account):
        pass

    def unbind(self, session, character):
        pass

    def shelve(self, session, character):
        pass

    def unshelve(self, session, character):
        pass
