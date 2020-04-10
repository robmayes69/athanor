from evennia.objects.objects import DefaultObject
from athanor.gamedb.base import AthanorBaseObjectMixin, AthanorExitMixin


class AthanorObject(AthanorBaseObjectMixin, DefaultObject):
    """
    Events Triggered:
        object_puppet (session): Fired whenever a Session puppets this object.
        object_disconnect (session): Triggered whenever a Session disconnects from this account.
        object_online (session): Fired whenever an account comes online from being completely offline.
        object_offline (session): Triggered when an account's final session closes.
    """
    dbtype = 'ObjectDB'


class AthanorRoom(AthanorObject):
    contents_categories = ['room']


class AthanorExit(AthanorExitMixin, AthanorObject):
    """
    Re-implements most of DefaultExit...
    """
    pass
