from evennia.abstracts.entity_base import TypeclassBase
from . models import EntityMapDB
from utils.events import EventEmitter


class EntityMap(EntityMapDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        EntityMapDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)

    def at_first_save(self):
        pass
