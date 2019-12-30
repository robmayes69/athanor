from evennia.objects.objects import DefaultCharacter
from athanor.core.gameentity import AthanorGameEntity
from athanor.core.submessage import SubMessageMixin

from athanor.typeclasses.scripts import GlobalScript
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from athanor.utils.color import green_yellow_red, red_yellow_green
from evennia.utils.utils import time_format
from evennia.utils.ansi import ANSIString
import datetime


class AthanorCharacter(DefaultCharacter, AthanorGameEntity, SubMessageMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)




class AthanorPlayerCharacter(AthanorCharacter):
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
