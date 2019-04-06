"""
Room

Rooms are simple containers that has no location of their own.

"""
from evennia import DefaultRoom
from athanor.utils.text import tabular_table
from athanor.utils.online import characters


class AthanorBaseRoom(DefaultRoom):
    """
    This class is a placeholder meant to represent deleted rooms. It implements the main room logic, but should
    not be used for new rooms.
    """
    pass


class AthanorRoom(AthanorBaseRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    pass
