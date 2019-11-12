from evennia.objects.objects import DefaultObject
from features.core.base import AthanorEntity
from evennia.utils.utils import lazy_property
from . submessage import SubMessageMixin
from . handler import KeywordHandler
from handlers.gear import GearHandler, InventoryHandler


class AthanorObject(DefaultObject, AthanorEntity, SubMessageMixin):

    def __init__(self, *args, **kwargs):
        DefaultObject.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)

    @lazy_property
    def keywords(self):
        return KeywordHandler(self)

    @lazy_property
    def gear(self):
        return GearHandler(self)

    @lazy_property
    def inventory(self):
        return InventoryHandler(self)