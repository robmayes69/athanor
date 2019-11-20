from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import lazy_property
from features.core.base import AthanorEntity
from features.core.submessage import SubMessageMixinCharacter
from features.core.handler import KeywordHandler
from handlers.gear import GearHandler, InventoryHandler
from typeclasses.scripts import GlobalScript
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace


class AthanorCharacter(DefaultCharacter, AthanorEntity, SubMessageMixinCharacter):

    def __init__(self, *args, **kwargs):
        DefaultCharacter.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)

    def get_gender(self, looker):
        return 'male'

    def system_msg(self, *args, **kwargs):
        if hasattr(self, 'account'):
            self.account.system_msg(*args, **kwargs)

    @lazy_property
    def keywords(self):
        return KeywordHandler(self)

    @lazy_property
    def gear(self):
        return GearHandler(self)

    @lazy_property
    def inventory(self):
        return InventoryHandler(self)


class AthanorPlayerCharacter(AthanorCharacter):
    pass


class AthanorShelvedCharacter(AthanorCharacter):
    pass


class AthanorMobileCharacter(AthanorCharacter):
    pass


class DefaultCharacterController(GlobalScript):
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

    def shelf_character(self):
        pass

    def unshelf_character(self):
        pass