"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from __future__ import unicode_literals
from django.conf import settings
from evennia import DefaultCharacter
from evennia.utils.utils import lazy_property
from athanor.handlers.base import CharacterTypeHandler
from athanor.styles.base import CharacterTypeStyle

from athanor.config.manager import GET_MANAGERS


class Character(DefaultCharacter):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """

    @lazy_property
    def ath(self):
        return CharacterTypeHandler(self)

    @lazy_property
    def styles(self):
        return CharacterTypeStyle(self)

    @lazy_property
    def managers(self):
        return GET_MANAGERS()

    def at_init(self):
        super(Character, self).at_init()
        for cmdset in settings.ATHANOR_CMDSETS_CHARACTER:
            self.cmdset.add(cmdset)

    def at_post_unpuppet(self, account, session=None):
        super(Character, self).at_post_unpuppet(account, session)
        self.ath.at_post_unpuppet(account, session)

        if not self.sessions.get():
            self.at_true_logout(account, session)

    def at_true_logout(self, account, session=None):
        """
        A sub-hook of at_post_unpuppet for scene that process only when all connected sessions disconnect.
        """
        self.ath.at_true_logout(account, session)

    def at_true_login(self):
        """
        This is called by at_post_puppet when a character with no previous sessions is puppeted.
        """
        self.ath.at_true_login()

    def at_post_puppet(self):
        super(Character, self).at_post_puppet()
        self.ath.at_post_puppet()

        if len(self.sessions.get()) == 1:
            self.at_true_login()

    def search_character(self, search_name=None, deleted=False):
        """
        Wrapper method for .search() for Characters only. Used by most Athanor code.

        Args:
            search_name (string) - Name to search for.

        Returns:
            ObjectDB instance.

        Raises:
            ValueError: If character cannot be found.

        """
        if not search_name:
            raise ValueError("Character name field empty.")

        # First, collect all possible character candidates.
        candidates = Character.objects.filter_family()

        # First we'll run an Exact check.:
        search_results = self.search(search_name, exact=True, use_nicks=True, candidates=candidates, quiet=True)

        # Did that not work? Next we'll try the online match if it's set!
        if not search_results and not deleted:
            characters = self.who.ndb.characters
            search_results = self.search(search_name, exact=False, use_nicks=True, candidates=characters,
                                         quiet=True)

        # We found NOBODY? Then error!
        if not search_results:
            raise ValueError("Character '%s' not found." % search_name)

        # We only want to return one result, even if multiple matches were found.
        if isinstance(search_results, list):
            return search_results[0]
        else:
            return search_results

