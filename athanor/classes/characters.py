import re
from collections import defaultdict
from django.conf import settings

from django.utils.translation import ugettext as _

from athanor.core.objects import AthanorObject
from evennia.utils.utils import class_from_module, lazy_property
from evennia.utils.logger import log_trace
from evennia.utils.ansi import ANSIString
from evennia.utils import logger

from athanor.entities.base import AbstractGameEntity
from athanor.core.submessage import SubMessageMixin
from athanor.core.scripts import AthanorGlobalScript
from athanor.utils.text import partial_match

from . models import CharacterBridge


class AthanorPlayerCharacter(AthanorObject, AbstractGameEntity, SubMessageMixin):
    lockstring = "puppet:id({character_id}) or pid({account_id}) or perm(Developer) or pperm(Developer);delete:id({account_id}) or perm(Admin)"


    persistent = True
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    def create_bridge(self, account, key, clean_key, namespace):
        if hasattr(self, 'character_bridge'):
            return
        char_bridge, created = CharacterBridge.objects.get_or_create(db_object=self, db_account=account,
                                                                     db_name=clean_key, db_cname=key,
                                                                     db_iname=clean_key.lower(), db_namespace=namespace)
        if created:
            char_bridge.save()

    @classmethod
    def create(cls, key, account, **kwargs):
        """
        Creates a basic Character with default parameters, unless otherwise
        specified or extended.

        Provides a friendlier interface to the utils.create_character() function.

        Args:
            key (str): Name of the new Character.
            account (obj): Account to associate this Character with. Required as
                an argument, but one can fake it out by supplying None-- it will
                change the default lockset and skip creator attribution.

        Kwargs:
            description (str): Brief description for this object.
            ip (str): IP address of creator (for object auditing).
            All other kwargs will be passed into the create_object call.

        Returns:
            character (Object): A newly created Character of the given typeclass.
            errors (list): A list of errors in string form, if any.

        """
        errors = []
        obj = None
        # Get IP address of creator, if available
        ip = kwargs.pop("ip", "")

        # If no typeclass supplied, use this class
        kwargs["typeclass"] = kwargs.pop("typeclass", cls)

        # Set the supplied key as the name of the intended object
        kwargs["key"] = key

        # Get home for character
        kwargs["home"] = ObjectDB.objects.get_id(
            kwargs.get("home", settings.DEFAULT_HOME)
        )

        # Get permissions
        kwargs["permissions"] = kwargs.get(
            "permissions", settings.PERMISSION_ACCOUNT_DEFAULT
        )

        # Get description if provided
        description = kwargs.pop("description", "")

        # Get locks if provided
        locks = kwargs.pop("locks", "")

        try:
            # Check to make sure account does not have too many chars
            if account:
                if len(account.characters) >= settings.MAX_NR_CHARACTERS:
                    errors.append(
                        "There are too many characters associated with this account."
                    )
                    return obj, errors

            # Create the Character
            obj = create.create_object(**kwargs)

            # Record creator id and creation IP
            if ip:
                obj.db.creator_ip = ip
            if account:
                obj.db.creator_id = account.id
                if obj not in account.characters:
                    account.db._playable_characters.append(obj)

            # Add locks
            if not locks and account:
                # Allow only the character itself and the creator account to puppet this character (and Developers).
                locks = cls.lockstring.format(
                    **{"character_id": obj.id, "account_id": account.id}
                )
            elif not locks and not account:
                locks = cls.lockstring.format(
                    **{"character_id": obj.id, "account_id": -1}
                )

            obj.locks.add(locks)

            # If no description is set, set a default description
            if description or not obj.db.desc:
                obj.db.desc = description if description else "This is a character."

        except Exception as e:
            errors.append("An error occurred while creating this '%s' object." % key)
            logger.log_err(e)

        return obj, errors

    @classmethod
    def create_character(cls, key, account, namespace=0, **kwargs):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Character Name.")
        if not cls.re_name.match(clean_key):
            raise ValueError("Character name does not meet standards. Avoid double spaces and special characters.")
        if namespace is not None:
            if CharacterBridge.objects.filter(db_iname=clean_key.lower(), db_namespace=namespace).count():
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

    def create_character(self, session, account, character_name, namespace=0):
        new_character = self.ndb.character_typeclass.create_character(character_name, account, namespace=namespace)
        new_character.db.account = account
        return new_character

    def delete_character(self):
        pass
