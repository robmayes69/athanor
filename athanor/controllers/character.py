from django.conf import settings

from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from evennia.utils.search import object_search

from athanor.controllers.base import AthanorController
from athanor.gamedb.characters import AthanorPlayerCharacter

from athanor.messages import character as cmsg

MIXINS = [class_from_module(mixin) for mixin in settings.CONTROLLER_MIXINS["CHARACTER"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorCharacterController(*MIXINS, AthanorController):
    system_name = 'CHARACTERS'

    def __init__(self, key, manager):
        AthanorController.__init__(self, key, manager)
        self.character_typeclass = None
        self.id_map = dict()
        self.name_map = dict()
        self.online = set()
        self.on_global("character_online", self.at_character_online)
        self.on_global("character_offline", self.at_character_offline)
        self.load()

    def do_load(self):
        try:
            self.character_typeclass = class_from_module(settings.BASE_CHARACTER_TYPECLASS,
                                                           defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.character_typeclass = AthanorPlayerCharacter

        self.update_cache()

    def at_character_online(self, sender, **kwargs):
        self.online.add(sender)

    def at_character_offline(self, sender, **kwargs):
        self.online.remove(sender)

    def update_cache(self):
        chars = AthanorPlayerCharacter.objects.filter_family(character_bridge__db_namespace=0)
        self.id_map = {char.id: char for char in chars}
        self.name_map = {char.key.upper(): char for char in chars}
        self.online = set(chars.exclude(db_account=None))

    def all(self):
        return AthanorPlayerCharacter.objects.filter_family()

    def search_all(self, name, exact=False):
        object_search(name, exact=exact, candidates=self.all())

    def find_character(self, character):
        if isinstance(character, AthanorPlayerCharacter):
            return character
        results = self.search_all(character)
        if not results:
            raise ValueError(f"Cannot locate character named {character}!")
        if len(results) == 1:
            return results[0]
        raise ValueError(f"That matched: {results}")

    def create_character(self, session, account, character_name, namespace=0, ignore_priv=False, location=None):
        if not (enactor := session.get_account()) or (not ignore_priv and not enactor.check_lock("apriv(character_create)")):
            raise ValueError("Permission denied.")
        if location is None:
            location = settings.DEFAULT_HOME
        account = self.manager.get('account').find_account(account)
        new_character = self.character_typeclass.create_character(character_name, account, namespace=namespace,
                                                                  location=location)
        new_character.db.account = account
        if namespace == 0:
            self.id_map[new_character.id] = new_character
            self.name_map[new_character.key.upper()] = new_character
        cmsg.CreateMessage(source=enactor, target=new_character, account_name=account.username).send()
        return new_character

    def delete_character(self, session, character, verify_name, ignore_priv=False):
        if not (enactor := session.get_account()) or (
                not ignore_priv and not enactor.check_lock("apriv(character_delete)")):
            raise ValueError("Permission denied.")
        character = self.find_character(character)
        account = character.bridge.account
        cmsg.DeleteMessage(source=enactor, target=character, account_name=account.username if account else 'N/A').send()

    def rename_character(self, session, character, new_name, ignore_priv=False):
        if not (enactor := session.get_account()) or (
                not ignore_priv and not enactor.check_lock("apriv(character_rename)")):
            raise ValueError("Permission denied.")
        character = self.find_character(character)
        account = character.bridge.account
        old_name = character.key
        new_name = character.rename(new_name)
        cmsg.RenameMessage(source=enactor, target=character, old_name=old_name, account_name=account.username).send()

    def transfer_character(self, session, character, new_account, ignore_priv=False):
        if not (enactor := session.get_account()) or (
                not ignore_priv and not enactor.check_lock("apriv(character_transfer)")):
            raise ValueError("Permission denied.")
        character = self.find_character(character)
        account = character.bridge.account
        new_account = self.manager.get('account').find_account(new_account)
        character.set_account(new_account)
        cmsg.TransferMessage(source=enactor, target=character, account_username=account.username,
                             new_account=new_account.username).send()
