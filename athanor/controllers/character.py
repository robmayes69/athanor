from django.conf import settings

from evennia.utils.utils import class_from_module, lazy_property
from evennia.utils.logger import log_trace

from athanor.gamedb.scripts import AthanorGlobalScript
from athanor.gamedb.characters import AthanorPlayerCharacter
from athanor.utils.text import partial_match

MIXINS = [class_from_module(mixin) for mixin in settings.CONTROLLER_MIXINS["CHARACTER"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))

class AthanorCharacterController(*MIXINS, AthanorGlobalScript):
    system_name = 'CHARACTERS'

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.character_typeclass = class_from_module(settings.BASE_CHARACTER_TYPECLASS,
                                                           defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.character_typeclass = AthanorPlayerCharacter

        self.update_cache()
        self.load()

    def do_load(self):
        self.on_global("character_online", self.at_character_online)
        self.on_global("character_offline", self.at_character_offline)

    def at_character_online(self, sender, **kwargs):
        self.ndb.online.add(sender)

    def at_character_offline(self, sender, **kwargs):
        self.ndb.online.remove(sender)

    def update_cache(self):
        chars = AthanorPlayerCharacter.objects.filter_family(character_bridge__db_namespace=0)
        self.ndb.id_map = {char.id: char for char in chars}
        self.ndb.name_map = {char.key.upper(): char for char in chars}
        self.ndb.online = set(chars.exclude(db_account=None))

    def find_character(self, character):
        if isinstance(character, AthanorPlayerCharacter):
            return character
        pass

    def create_character(self, session, account, character_name, namespace=0):
        new_character = self.ndb.character_typeclass.create_character(character_name, account, namespace=namespace)
        new_character.db.account = account
        if namespace == 0:
            self.ndb.id_map[new_character.id] = new_character
            self.ndb.name_map[new_character.key.upper()] = new_character
        return new_character

    def delete_character(self):
        pass
