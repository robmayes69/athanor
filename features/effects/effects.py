from evennia.typeclasses.models import TypeclassBase
from . models import EffectDefinitionDB, EffectValueDB
from utils.events import EventEmitter
from features.core.handler import AthanorFlexHandler


class DefaultEffectDefinition(EffectDefinitionDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        EffectDefinitionDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultEffectValue(EffectValueDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        EffectValueDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class EffectHandler(AthanorFlexHandler):
    model_class = EffectValueDB
