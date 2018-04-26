"""
Contains the base framework for Athanor's Managers. When Managers load, they instantiate all of their
respective Handlers for that Typeclass base.

Managers are available on characters, accounts, and sessions via their .ath property.
"""
import athanor


class __BaseManager(object):
    """
    The base used for the Athanor Managers that are loaded onto all Athanor Accounts and Characters.

    Not meant to be used directly.
    """
    mode = None

    def get_handlers(self):
        pass

    def __init__(self, owner):
        """

        :param owner: An instance of a TypeClass'd object.
        """

        self.owner = owner
        self.attributes = owner.attributes

        # Make validators available to TypeManagers!
        self.valid = athanor.VALIDATORS

        # Load all handlers.
        handlers = athanor.HANDLERS_SORTED[self.mode]
        self.ordered_handlers = list()
        self.handlers = dict()
        for handler in handlers:
            loaded_handler = handler(self)
            self.handlers[handler.key] = loaded_handler
            self.ordered_handlers.append(loaded_handler)

        # Call an extensible Load function for simplicity if need be.
        self.load()

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
        return self.handlers[item]

    def accept_request(self, request):
        self.handlers[request.handler].accept_request(request)
