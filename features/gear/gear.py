from evennia.typeclasses.models import TypeclassBase
from . models import InventoryDB, InventorySlotDB, GearSetDB, GearSlotDB
from utils.events import EventEmitter


class DefaultInventory(InventoryDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        InventoryDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultInventorySlot(InventorySlotDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        InventorySlotDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultGearSet(GearSetDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        GearSetDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class DefaultGearSlot(GearSlotDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        GearSlotDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)