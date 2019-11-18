from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import lazy_property
from features.core.base import AthanorEntity
from . submessage import SubMessageMixinCharacter
from . handler import KeywordHandler
from handlers.gear import GearHandler, InventoryHandler


class AthanorCharacter(DefaultCharacter, AthanorEntity, SubMessageMixinCharacter):

    def __init__(self, *args, **kwargs):
        DefaultCharacter.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)

    def get_gender(self, looker):
        return 'male'

    def system_msg(self, *args, **kwargs):
        if hasattr(self, 'account'):
            self.account.system_msg(*args, **kwargs)

    @lazy_property
    def keywords(self):
        return KeywordHandler(self)

    @lazy_property
    def gear(self):
        return GearHandler(self)

    @lazy_property
    def inventory(self):
        return InventoryHandler(self)


class AthanorPlayerCharacter(AthanorCharacter):
    pass


class AthanorMobileCharacter(AthanorCharacter):
    pass
