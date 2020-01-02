from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from evennia.utils.ansi import ANSIString

from athanor.core.gameentity import AthanorGameEntity
from athanor.core.submessage import SubMessageMixin
from athanor.core.scripts import AthanorGlobalScript

from . models import CharacterBridge


class AthanorCharacter(DefaultCharacter, AthanorGameEntity, SubMessageMixin):
    pass


class AthanorPlayerCharacter(AthanorCharacter):

    def create_bridge(self, account, key, clean_key):
        if hasattr(self, 'character_bridge'):
            return
        char_bridge, created = CharacterBridge.objects.get_or_create(db_object=self, db_account=account,
                                                                     db_name=clean_key, db_cname=key,
                                                                     db_iname=clean_key.lower())
        if created:
            char_bridge.save()

    @classmethod
    def create_character(cls, key, account, **kwargs):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Character Name.")
        if CharacterBridge.objects.filter(db_iname=clean_key.lower()).count():
            raise ValueError("Name conflicts with another Character.")
        character, errors = cls.create(key, account, **kwargs)
        character.create_bridge(account, key, clean_key)
        bridge, created = CharacterBridge.objects.get_or_create(db_account=account, db_object=character,
                                                                db_name=key, db_iname=key.lower())
        if created:
            bridge.save()
        return character, errors

    def rename(self, key):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Character Name.")
        bridge = self.character_bridge
        if CharacterBridge.objects.filter(db_iname=clean_key.lower()).exclude(id=bridge).count():
            raise ValueError("Name conflicts with another Character.")
        self.key = clean_key
        bridge.db_name = clean_key
        bridge.db_iname = clean_key.lower()
        bridge.db_cname = key


class AthanorMobileCharacter(AthanorCharacter):
    pass


class AthanorCharacterController(AthanorGlobalScript):
    system_name = 'CHARACTERS'

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.character_typeclass = class_from_module(settings.BASE_CHARACTER_TYPECLASS,
                                                           defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.character_typeclass = AthanorPlayerCharacter

    def find_character(self, character):
        if isinstance(character, AthanorPlayerCharacter):
            return character
        pass

    def create_character(self, session, account, character_name):
        new_character, errors = self.ndb.character_typeclass.create(character_name, account)
        if errors:
            raise ValueError(f"Error Creating {account} - {character_name}: {str(errors)}")
        new_character.db.account = account
        return new_character, errors

    def delete_character(self):
        pass
