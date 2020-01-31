from django.conf import settings

from evennia.objects.objects import DefaultObject
from evennia.utils.utils import class_from_module

from athanor.gamedb.base import AthanorBaseObjectMixin, AthanorExitMixin

MIXINS = [class_from_module(mixin) for mixin in settings.GAMEDB_MIXINS["OBJECT"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorObject(*MIXINS, AthanorBaseObjectMixin, DefaultObject):
    """
    Events Triggered:
        object_puppet (session): Fired whenever a Session puppets this object.
        object_disconnect (session): Triggered whenever a Session disconnects from this account.
        object_online (session): Fired whenever an account comes online from being completely offline.
        object_offline (session): Triggered when an account's final session closes.
    """
    pass


class AthanorRoom(AthanorObject):
    contents_categories = ['room']


class AthanorExit(AthanorExitMixin, AthanorObject):
    """
    Re-implements most of DefaultExit...
    """
    pass
