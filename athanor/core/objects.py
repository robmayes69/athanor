from evennia.objects.objects import DefaultObject
from features.core.base import AthanorEntity
from evennia.utils.utils import lazy_property
from . submessage import SubMessageMixin
from . handler import KeywordHandler


class AthanorObject(DefaultObject, AthanorEntity, SubMessageMixin):

    def __init__(self, *args, **kwargs):
        DefaultObject.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)

    @lazy_property
    def keywords(self):
        return KeywordHandler(self)