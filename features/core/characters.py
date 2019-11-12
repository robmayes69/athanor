from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import lazy_property
from utils.events import EventEmitter
from . submessage import SubMessageMixinCharacter
from . handler import KeywordHandler


class AthanorCharacter(DefaultCharacter, EventEmitter, SubMessageMixinCharacter):

    def __init__(self, *args, **kwargs):
        DefaultCharacter.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)

    def get_gender(self, looker):
        return 'male'

    @lazy_property
    def keywords(self):
        return KeywordHandler(self)


class AthanorPlayerCharacter(AthanorCharacter):
    pass


class AthanorMobileCharacter(AthanorCharacter):
    pass
