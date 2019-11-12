from evennia.objects.objects import DefaultObject
from utils.events import EventEmitter
from evennia.utils.utils import lazy_property
from . submessage import SubMessageMixin
from . handler import KeywordHandler


class AthanorObject(DefaultObject, EventEmitter, SubMessageMixin):

    def __init__(self, *args, **kwargs):
        DefaultObject.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)

    @lazy_property
    def keywords(self):
        return KeywordHandler(self)
