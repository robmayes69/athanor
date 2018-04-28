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

        # Make validators, systems, and properties available to TypeManagers!
        self.valid = athanor.VALIDATORS

        self.systems = athanor.SYSTEMS

        self.properties = athanor.PROPERTIES_DICT[self.mode]

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