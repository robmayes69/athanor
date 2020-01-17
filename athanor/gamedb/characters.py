import re

from django.conf import settings
from evennia.utils.utils import class_from_module
from evennia.utils.ansi import ANSIString

from athanor.gamedb.objects import AthanorObject
from athanor.models import CharacterBridge

MIXINS = []

for mixin in settings.MIXINS["CHARACTER"]:
    MIXINS.append(class_from_module(mixin))
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorPlayerCharacter(*MIXINS, AthanorObject):
    """
    The basic Athanor Player Character, built atop of Evennia's DefaultObject but modified to co-exist with Entities
    and exist in the Athanor Grid system.
    """
    lockstring = "puppet:id({character_id}) or pid({account_id}) or perm(Developer) or pperm(Developer);delete:id({account_id}) or perm(Admin)"
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    def create_bridge(self, account, key, clean_key, namespace):
        if hasattr(self, 'character_bridge'):
            return
        CharacterBridge.objects.get_or_create(db_object=self, db_account=account, db_name=clean_key, db_cname=key,
                                              db_iname=clean_key.lower(), db_namespace=namespace)

    @classmethod
    def create_character(cls, key, account, namespace=0, **kwargs):
        """
        Create a character! Also creates extra models and sets everything up.
        This is meant to be called by the Character Controller, not directly.

        Args:
            key (str or ANSIString): The name of the character to be created.
            account (AccountDB): The account that will own the character.
            namespace (int or None): Characters that belong to the same namespace will check for name
                uniqueness, case insensitive. If namespace is None, then there is no integrity checking.
            **kwargs:

        Returns:
            Character (ObjectDB)
        """
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Character Name.")
        if not cls.re_name.match(clean_key):
            raise ValueError("Character name does not meet standards. Avoid double spaces and special characters.")
        if namespace is not None and CharacterBridge.objects.filter(db_iname=clean_key.lower(), db_namespace=namespace).count():
            raise ValueError("Name conflicts with another Character.")
        character, errors = cls.create(clean_key, account, **kwargs)
        if character:
            character.create_bridge(account, key, clean_key, namespace)
        else:
            raise ValueError(errors)
        return character

    def rename(self, key):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Character Name.")
        if not self.re_name.match(clean_key):
            raise ValueError("Character name does not meet standards. Avoid double spaces and special characters.")
        bridge = self.character_bridge
        if CharacterBridge.objects.filter(db_iname=clean_key.lower()).exclude(id=bridge).count():
            raise ValueError("Name conflicts with another Character.")
        self.key = clean_key
        bridge.db_name = clean_key
        bridge.db_iname = clean_key.lower()
        bridge.db_cname = key

    def basetype_setup(self):
        AthanorObject.basetype_setup(self)
        self.locks.add(
            ";".join(["get:false()", "call:false()"])  # noone can pick up the character
        )  # no commands can be called on character from outside
        # add the default cmdset
        self.cmdset.add_default(settings.CMDSET_CHARACTER, permanent=True)

    def at_after_move(self, source_location, **kwargs):
        """
        We make sure to look around after a move.

        """
        if self.location.access(self, "view"):
            self.msg(self.at_look(self.location))


