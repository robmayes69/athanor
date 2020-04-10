import re
import time

from django.conf import settings
from evennia.utils.ansi import ANSIString

from athanor.gamedb.objects import AthanorObject
from athanor.models import CharacterBridge, ObjectNamespace, LocationStorage
from athanor.gamedb.base import AthanorBasePlayerMixin


class AthanorPlayerCharacter(AthanorBasePlayerMixin, AthanorObject):
    """
    The basic Athanor Player Character. Note that Athanor uses the Character as a 'relatable container' and master of
    puppets. It is not meant to enter the game world directly. For that, see Avatars.

    Connect/Puppet Trigger prefixes are 'object' and 'character'.
    """
    lockstring = "puppet:pid({account_id}) or pperm(Developer);delete:pperm(Developer)"
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    def create_bridge(self, account, key, clean_key, namespace):
        """
        Creates the Django Model that will hold extra information about Player Characters.

        Args:
            account (AccountDB): The Account that owns this character.
            key (str): The character's name, possibly including color codes.
            clean_key (str): The character's name without color codes.
            namespace (int or None): Characters of a matching namespace have enforced name uniqueness.
                Enter None to disable namespace checking, but this is intended for retired/soft deleted.

        Returns:
            None
        """
        if hasattr(self, 'character_bridge'):
            return
        CharacterBridge.objects.get_or_create(db_object=self, db_account=account, db_name=clean_key, db_cname=key,
                                              db_iname=clean_key.lower(), db_namespace=namespace)

    @classmethod
    def create_character(cls, key, account, namespace='player_characters', **kwargs):
        """
        Create a character! Also creates extra models and sets everything up.
        This is meant to be called by the Character Controller, not directly.

        Args:
            key (str or ANSIString): The name of the character to be created.
            account (AccountDB): The account that will own the character.
            namespace (int or None): Characters that belong to the same namespace will check for name
                uniqueness, case insensitive. If namespace is None, then there is no integrity checking.
            **kwargs: Will be passed through to cls.create()

        Returns:
            Character (ObjectDB)
        """
        if not key:
            raise ValueError("Characters must have a name!")
        if not account:
            raise ValueError("Characters must belong to an Account!")
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Character Name.")
        if not cls.re_name.match(clean_key):
            raise ValueError("Character name does not meet standards. Avoid double spaces and special characters.")
        namespace_name, created = ObjectNamespaceName.objects.get_or_create(db_name=namespace)
        if created:
            namespace_name.save()
        if namespace is not None and CharacterBridge.objects.filter(db_iname=clean_key.lower(), db_namespace=namespace_name).count():
            raise ValueError("Name conflicts with another Character.")
        character, errors = cls.create(clean_key, account, **kwargs)
        if character:
            character.create_bridge(account, key, clean_key, namespace_name)
        else:
            raise ValueError(errors)
        return character

    def rename(self, key):
        """
        Renames a character and updates all relevant fields.

        Args:
            key (str): The character's new name. Can include ANSI codes.

        Returns:
            key (ANSIString): The successful key set.
        """
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Character Name.")
        if not self.re_name.match(clean_key):
            raise ValueError("Character name does not meet standards. Avoid double spaces and special characters.")
        bridge = self.character_bridge
        namespace, created = ObjectNamespaceName.objects.get_or_create(db_name='player_characters')
        if created:
            namespace.save()
        if namespace.objects.filter(db_iname=clean_key.lower(), db_namespace=namespace).exclude(db_object=self).count():
            raise ValueError("Name conflicts with another Character.")
        self.key = clean_key
        bridge.db_name = clean_key
        bridge.db_iname = clean_key.lower()
        bridge.db_cname = key
        bridge.save(update_fields=['db_name', 'db_iname', 'db_cname'])
        return key

    def basetype_setup(self):
        """
        Mostly just re-implementing DefaultCharacter's BaseType setup from Evennia.

        Returns:
            None
        """
        AthanorObject.basetype_setup(self)
        self.locks.add(
            ";".join(["get:false()", "call:false()"])  # noone can pick up the character
        )  # no commands can be called on character from outside
        # add the default cmdset
        self.cmdset.add_default(settings.CMDSET_CHARACTER, permanent=True)

    def archive(self):
        """
        Places this character into the Archives. An Archived character no longer participates in the
        character namespace, cannot be logged into, etc. It's effectively a soft-deletion.

        Returns:
            None
        """
        self.namespace.set_namespace(None)
        self.at_archive()

    def at_archive(self):
        """
        Called whenever a character is archived.

        Returns:
            None
        """
        pass

    def restore(self, replace_name):
        """
        Restores an archived character to playability.

        Args:
            replace_name (str): Since an archived character's name might be taken in the main namespace,
                this is used as an alternative if necessary.

        Returns:
            None
        """
        old_name = self.key
        if not replace_name:
            try:
                self.namespace.set_namespace('player_characters')
            except Exception as e:
                raise ValueError("Cannot restore character. Does another character use the same name?")
        else:
            self.rename(replace_name)
            self.namespace.set_namespace("player_characters")
        self.at_restore(old_name, replace_name)

    def at_restore(self, old_name, replace_name):
        """
        Called when a character is restored.

        Args:
            old_name (str): The character's name before restoration.
            replace_name (str or None): The character's replacement name, if any.

        Returns:
            None
        """
        pass

    def set_account(self, new_account):
        account = self.bridge.account
        self.bridge.account = new_account
        self.at_transfer(account)

    def at_transfer(self, old_account):
        """
        Called whenever a character is transferred to a different account.

        Args:
            old_account (AccountDB): The previous Account that owned this character.

        Returns:
            None
        """
        pass

    @property
    def idle_time(self):
        """
        Returns the idle time of the least idle session in seconds. If
        no sessions are connected it returns nothing.
        """
        idle = [session.cmd_last_visible for session in self.sessions.all()]
        if idle:
            return time.time() - float(max(idle))
        return None

    @property
    def connection_time(self):
        """
        Returns the maximum connection time of all connected sessions
        in seconds. Returns nothing if there are no sessions.
        """
        conn = [session.conn_time for session in self.sessions.all()]
        if conn:
            return time.time() - float(min(conn))
        return None