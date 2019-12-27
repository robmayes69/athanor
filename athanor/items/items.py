from evennia.typeclasses.models import TypeclassBase
from . models import MarketDB, ItemDefinitionDB, InventoryDB, ItemDB
from features.core.base import AthanorTypeEntity
from features.core.handler import AthanorFlexHandler
from evennia.typeclasses.managers import TypeclassManager


class DefaultMarket(MarketDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        MarketDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultItemDefinition(ItemDefinitionDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        ItemDefinitionDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultInventory(InventoryDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        InventoryDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultItem(ItemDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        ItemDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultInventoryHandler(AthanorFlexHandler):
    model_class = DefaultInventory

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