from evennia.typeclasses.models import TypeclassBase
from . models import EffectDB
from utils.events import EventEmitter


class DefaultEffect(EffectDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        EffectDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)
