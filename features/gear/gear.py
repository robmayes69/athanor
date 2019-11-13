from evennia.typeclasses.models import TypeclassBase
from . models import InventoryDB, InventorySlotDB, GearSetDB, GearSlotDB
from features.core.base import AthanorTypeEntity
from features.core.handler import AthanorFlexHandler


class DefaultInventory(InventoryDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        InventoryDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultInventorySlot(InventorySlotDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        InventorySlotDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultGearSet(GearSetDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        GearSetDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultGearSlot(GearSlotDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        GearSlotDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultInventoryHandler(AthanorFlexHandler):
    model_class = DefaultInventorySlot
    model_definition = DefaultInventory

    def add(self, inventory, item, slot=None, force=False):
        find = self.model_definition.objects.filter(db_key=inventory).first()
        if not find:
            raise ValueError(f"No inventory named '{inventory}'!")
        if not force and not find.can_add_item(self, item, slot):
            pass
        if not force and not self.can_add_item(item, slot):
            pass
        if not force and not item.can_enter_inventory(self):
            pass

    def can_add_item(self, item, slot, force=False):
        pass

    def remove(self, inventory, item):
        pass

    def can_remove_item(self, inventory, item, force=False):
        pass

    def swap(self, inventory, from_slot, to_slot):
        pass


class DefaultGearHandler(AthanorFlexHandler):
    model_class = DefaultGearSlot
    model_definition = DefaultGearSet
