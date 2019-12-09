from evennia.characters.characters import DefaultCharacter
from features.core.base import AthanorEntity
from evennia.utils.utils import lazy_property
from . submessage import SubMessageMixin
from . handler import KeywordHandler


class AthanorObject(DefaultCharacter, AthanorEntity, SubMessageMixin):

    def __init__(self, *args, **kwargs):
        DefaultCharacter.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)

    @lazy_property
    def keywords(self):
        return KeywordHandler(self)