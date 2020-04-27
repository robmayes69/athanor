import re
from evennia.utils.search import object_search

from athanor.utils.controllers import AthanorController, AthanorControllerBackend
from athanor.playercharacters.playercharacters import DefaultPlayerCharacter

from athanor.playercharacters import messages as cmsg


class AthanorPlayerCharacterController(AthanorController):
    system_name = 'CHARACTERS'

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def find_character(self, character, archived=False):
        return self.backend.find_character(character, archived=archived)

    find_user = find_character

    def create_character(self, session, account, character_name, ignore_priv=False, typeclass=None, no_session=False):
        if not session and not no_session:
            raise ValueError("Permission denied.")
        if session and not no_session:
            if not (enactor := session.get_account()) or (not ignore_priv and not enactor.check_lock("oper(character_create)")):
                raise ValueError("Permission denied.")
        else:
            enactor = account
        account = self.manager.get('account').find_account(account)
        new_character = self.backend.create_character(account, character_name, typeclass=typeclass)
        entities = {'enactor': enactor, 'character': new_character, 'account': account}
        cmsg.CreateMessage(entities).send()
        return new_character

    def archive_character(self, session, character, verify_name):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise ValueError("Permission denied.")
        character = self.find_character(character)
        account = character.character_bridge.account
        character.archive()
        entities = {'enactor': enactor, 'character': character, 'account': account}
        cmsg.ArchiveMessage(entities).send()
        character.force_disconnect(reason="Character has been archived!")

    def restore_character(self, session, character, replace_name):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise ValueError("Permission denied.")
        character = self.find_character(character)
        account = character.character_bridge.account
        character.restore(replace_name)
        entities = {'enactor': enactor, 'character': character, 'account': account}
        cmsg.RestoreMessage(entities).send()

    def rename_character(self, session, character, new_name, ignore_priv=False):
        if not (enactor := session.get_account()) or (
                not ignore_priv and not enactor.check_lock("pperm(Admin)")):
            raise ValueError("Permission denied.")
        character = self.find_character(character)
        account = character.character_bridge.account
        old_name = character.key
        new_name = character.rename(new_name)
        entities = {'enactor': enactor, 'character': character, 'account': account}
        cmsg.RenameMessage(entities, old_name=old_name).send()

    def transfer_character(self, session, character, new_account, ignore_priv=False):
        if not (enactor := session.get_account()) or (
                not ignore_priv and not enactor.check_lock("pperm(Admin)")):
            raise ValueError("Permission denied.")
        character = self.find_character(character)
        account = character.character_bridge.account
        new_account = self.manager.get('account').find_account(new_account)
        character.force_disconnect(reason="This character has been transferred to a different account!")
        character.set_account(new_account)
        entities = {'enactor': enactor, 'character': character, 'account_from': account, 'account_to': new_account}
        cmsg.TransferMessage(entities).send()

    def examine_character(self, session, character):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise ValueError("Permission denied.")
        character = self.find_character(character)
        return character.render_examine(enactor)

    def list_characters(self, session, archived=False):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise ValueError("Permission denied.")
        if not (characters := self.all() if not archived else self.archived()):
            raise ValueError("No characters to list!")
        styling = enactor.styler
        message = [
            styling.styled_header(f"{'Character' if not archived else 'Archived Character'} Listing")
        ]
        for char in characters:
            message.extend(char.render_list_section(enactor, styling))
        message.append(styling.blank_footer)
        return '\n'.join(str(l) for l in message)

    def all(self, account=None):
        return self.backend.all(account=account)


class AthanorPlayerCharacterControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('player_character_typeclass', 'BASE_PLAYER_CHARACTER_TYPECLASS', DefaultPlayerCharacter)
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.player_character_typeclass = None
        self.id_map = dict()
        self.name_map = dict()
        self.online = set()
        self.reg_names = None
        self.load()

    def do_load(self):
        self.update_cache()

    def update_regex(self):
        escape_names = [re.escape(name) for name in self.name_map.keys()]
        self.reg_names = re.compile(r"(?i)\b(?P<found>%s)\b" % '|'.join(escape_names))

    def update_cache(self):
        chars = DefaultPlayerCharacter.objects.filter_family()
        self.id_map = {char.pk: char for char in chars}
        self.name_map = {char.key.upper(): char for char in chars}
        self.online = set(chars.exclude(db_account=None))

    def all(self, account=None):
        if account is None:
            return DefaultPlayerCharacter.objects.filter_family()
        return DefaultPlayerCharacter.objects.filter_family(db_account=account)

    def count(self):
        return DefaultPlayerCharacter.objects.filter_family().count()

    def find_player_character(self, character, archived=False):
        if isinstance(character, DefaultPlayerCharacter):
            return character
        results = self.search_all(character) if not archived else self.search_archived(character)
        if not results:
            raise ValueError(f"Cannot locate character named {character}!")
        if len(results) == 1:
            return results[0]
        raise ValueError(f"That matched: {results}")

    def search_all(self, name, exact=False, candidates=None):
        if candidates is None:
            candidates = self.all()
        return object_search(name, exact=exact, candidates=self.all())

    def archived(self):
        return self.all()

    def search_archived(self, name, exact=False):
        return self.search_all(name, exact, candidates=self.archived())

    def create_character(self, account, character_name, typeclass=None):
        if not typeclass:
            typeclass = self.player_character_typeclass
        new_character = typeclass.create_playercharacter(account, character_name)
        self.id_map[new_character.id] = new_character
        self.name_map[new_character.key.lower()] = new_character
        return new_character
