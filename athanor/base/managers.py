"""
Contains the base framework for Athanor's Managers. When Managers load, they instantiate all of their
respective Handlers for that Typeclass base.

Managers are available on characters, accounts, and sessions via their .ath property.
"""
import athanor
import math
from evennia.utils.ansi import ANSIString
from evennia.utils.evtable import EvTable


class __BaseManager(object):
    """
    The base used for the Athanor Managers that are loaded onto all Athanor Accounts and Characters.

    Not meant to be used directly.
    """
    mode = None

    def get_helpers(self):
        pass

    def __init__(self, owner):
        """

        :param owner: An instance of a TypeClass'd object.
        """

        self.owner = owner
        self.attributes = owner.attributes

        # Load all helpers.
        helpers = getattr(athanor.LOADER, 'helpers_%s' % self.mode)
        self.ordered_helpers = list()
        self.helpers = dict()
        for helper in helpers:
            loaded_helper = helper(self)
            self.helpers[helper.key] = loaded_helper
            self.ordered_helpers.append(loaded_helper)
        for helper in self.ordered_helpers:
            helper.load_final()

        # Call an extensible Load function for simplicity if need be.
        self.load()

    @property
    def valid(self):
        return athanor.LOADER.validators

    @property
    def systems(self):
        return athanor.LOADER.systems

    @property
    def properties(self):
        return getattr(athanor.LOADER, 'properties_%s' % self.mode)

    @property
    def settings(self):
        return athanor.LOADER.settings

    @property
    def styles(self):
        return athanor.LOADER.styles

    def load(self):
        """
        By default this does nothing. It's meant to be overloaded by a sub-class.

        Returns:
            None
        """
        pass

    def __getitem__(self, item):
        """
        Implements dictionary-like lookups for Handler keys on the manager.
        Args:
            item:

        Returns:

        """
        return self.helpers[item]

    def accept_request(self, request):
        self.helpers[request.helper].accept_request(request)

    def prop(self, key, viewer, *args, **kwargs):
        """
        Retrieve and format a property of the owner for viewer's pleasure.

        Args:
            key (str): The key of the Property function to run.
            viewer (session): A session instance that's doing the checking.

        Returns:
            Something that can be printed. This method is meant to be used for formatting tables and etc.
        """
        return self.properties[key](self.owner, viewer, *args, **kwargs)


class AccountManager(__BaseManager):
    """
    Athanor basic Account Manager.

    Implements all of the Account hooks that Handlers need.
    """
    mode = 'account'

    def at_account_creation(self):
        for helper in self.ordered_helpers:
            helper.at_account_creation()

    def at_post_login(self, session, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_post_login(session, **kwargs)

    def at_true_login(self, session, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_true_login(session, **kwargs)

    def at_failed_login(self, session, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_failed_login(session, **kwargs)

    def at_init(self):
        for helper in self.ordered_helpers:
            helper.at_init()

    def at_disconnect(self, reason, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_disconnect(reason, **kwargs)

    def at_true_logout(self, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_true_logout(**kwargs)

    def render_login(self, session, viewer):
        message = []
        for helper in self.ordered_helpers:
            message.append(helper.render_login(session, viewer))
        return '\n'.join([str(line) for line in message if line])


class SessionManager(__BaseManager):
    mode = 'session'

    def at_sync(self):
        for helper in self.ordered_helpers:
            helper.at_sync()

    def at_login(self, account, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_login(account, **kwargs)

    def at_disconnect(self, reason, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_disconnect(reason, **kwargs)


class CharacterManager(__BaseManager):
    """
    Athanor basic Character Manager.

    Implements all of the Character hooks that Handlers need.
    """
    mode = 'character'

    def at_object_creation(self):
        for helper in self.ordered_helpers:
            helper.at_object_creation()

    def at_init(self):
        for helper in self.ordered_helpers:
            helper.at_init()

    def at_post_unpuppet(self, account, session, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_post_unpuppet(account, session, **kwargs)

    def at_true_logout(self, account, session, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_true_logout(account, session, **kwargs)

    def at_true_login(self, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_true_login(**kwargs)

    def at_post_puppet(self, **kwargs):
        for helper in self.ordered_helpers:
            helper.at_post_puppet(**kwargs)


class RenderManager(__BaseManager):
    """
    Special Manager used purely for rendering output displays.
    """
    mode = 'render'

