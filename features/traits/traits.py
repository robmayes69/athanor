from evennia.typeclasses.models import TypeclassBase
from . models import TraitDefinitionDB, TraitValueDB
from utils.events import EventEmitter


class DefaultTraitDefinition(TraitDefinitionDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        TraitDefinitionDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultTraitValue(TraitValueDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        TraitValueDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)
