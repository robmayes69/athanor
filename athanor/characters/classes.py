"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from evennia.utils.utils import lazy_property
from athanor.characters.managers import CharacterManager
from athanor import AthException


# This implements the Athanor API, but the base Typeclass should be Character, below.
class BaseCharacter(DefaultCharacter):
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
        return CharacterManager(self)

    def at_init(self):
        super(BaseCharacter, self).at_init()
        self.ath.at_init()

    def at_object_creation(self):
        self.ath.at_object_creation()

    def at_post_unpuppet(self, account, session=None, **kwargs):
        self.ath.at_post_unpuppet(account, session)

        if not self.sessions.count():
            self.at_true_logout(account, session)

    def at_true_logout(self, account, session=None, **kwargs):
        """
        A sub-hook of at_post_unpuppet for scene that process only when all connected sessions disconnect.
        """
        self.db.prelogout_location = self.location
        self.location = None
        self.ath.at_true_logout(account, session)

    def at_true_login(self, **kwargs):
        """
        This is called by at_post_puppet when a character with no previous sessions is puppeted.
        """
        self.ath.at_true_login(**kwargs)

    def at_post_puppet(self, **kwargs):
        session = self.sessions.get()[-1]
        if self.location:
            self.msg((self.at_look(session, self.location), {'type':'look'}), options = None)
        self.ath.at_post_puppet(session=session)

        if self.sessions.count() == 1:
            self.at_true_login(session=session)

    def at_look(self, session, target, **kwargs):
        """
        Called when this object performs a look. It allows to
        customize just what this means. It will not itself
        send any data.

        Args:
            session (session): The session initiating the look.
                This is required for formatting rules purposes.
            target (Object): The target being looked at. This is
                commonly an object or the current location. It will
                be checked for the "view" type access.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            lookstring (str): A ready-processed look string
                potentially ready to return to the looker.


        # Re-implemented for Athanor to pass Session data so FORMATTING RULES and stuff.
        """
        if not target.access(self, "view"):
            try:
                return "Could not view '%s'." % target.get_display_name(self)
            except AttributeError:
                return "Could not view '%s'." % target.key

        description = target.return_appearance(session, self)

        # the target's at_desc() method.
        # this must be the last reference to target so it may delete itself when acted on.
        target.at_desc(looker=self)

        return description

    def search_character(self, search_name=None, deleted=False):
        """
        Wrapper method for .search() for Characters only. Used by most Athanor code.

        Args:
            search_name (string) - Name to search for.

        Returns:
            ObjectDB instance.

        Raises:
            AthException: If character cannot be found.

        """
        if not search_name:
            raise AthException("Character name field empty.")

        # First, collect all possible character candidates.
        candidates = self.__class__.objects.filter_family()

        # First we'll run an Exact check.:
        search_results = self.search(search_name, exact=True, use_nicks=True, candidates=candidates, quiet=True)

        # Did that not work? Next we'll try the online match if it's set!
        if not search_results and not deleted:
            characters = self.who.ndb.characters
            search_results = self.search(search_name, exact=False, use_nicks=True, candidates=characters,
                                         quiet=True)

        # We found NOBODY? Then error!
        if not search_results:
            raise AthException("Character '%s' not found." % search_name)

        # We only want to return one result, even if multiple matches were found.
        if isinstance(search_results, list):
            return search_results[0]
        else:
            return search_results

    def return_appearance(self, session, viewer):
        return "TO BE IMPLEMENTED"

# This is a separate, special branch off of BaseCharacter. It implements the Athanor API, but exists only for
# characters that are no longer in use.
class ShelvedCharacter(BaseCharacter):
    pass


# This is the character class Athanor uses for all its hard work. If you're gonna subclass, subclass from this.
class Character(BaseCharacter):
    pass
