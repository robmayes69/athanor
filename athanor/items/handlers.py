from django.conf import settings
from evennia.utils.utils import class_from_module


class ItemHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.inventories = dict()

    @property
    def contents(self):
        all = set()
        for inv in self.inventories.values():
            all += inv.contents
        return list(all)

    def all(self, inv_name=None):
        if not inv_name:
            return self.contents
        else:
            if inv_name in self.inventories:
                return self.inventories[inv_name].all()
            else:
                return list()

    def get_inventory(self, inv_name):
        if (found := self.inventories.get(inv_name, None)):
            return found
        inv_class = class_from_module(settings.SPECIAL_INVENTORY_CLASSES.get(inv_name, settings.BASE_INVENTORY_CLASS))
        new_inv = inv_class(self, inv_name)
        self.inventories[inv_name] = new_inv
        return new_inv

    def can_add(self, entity, inv_name):
        if entity in self.contents:
            raise ValueError(f"{self.owner} is already carrying {entity}!")
        inv = self.get_inventory(inv_name)
        for aspect in self.owner.aspects.all():
            if not aspect.at_before_get(entity, inv):
                raise ValueError(f"{aspect} does not allow getting {entity}!")
        inv.can_add(entity)

    def can_transfer(self, entity, inv_name):
        if entity not in self.contents:
            raise ValueError(f"{self.owner} is not carrying {entity}!")
        old_inv = entity.inventory_location
        old_inv.can_remove(entity)
        inv = self.get_inventory(inv_name)
        inv.can_add(entity)

    def can_remove(self, entity):
        if entity not in self.contents:
            raise ValueError(f"{self.owner} is not carrying {entity}!")
        old_inv = entity.inventory_location
        old_inv.can_remove(entity)

    def add(self, entity, inv_name=None, run_checks=True):
        if not inv_name:
            inv_name = entity.default_inventory
        if run_checks:
            self.can_add(entity, inv_name)
        inv = self.get_inventory(inv_name)
        inv.add(entity)
        self.contents.add(entity)

    def transfer(self, entity, inv_name, run_checks=True):
        if run_checks:
            self.can_transfer(entity, inv_name)
        dest = self.get_inventory(inv_name)
        inv = entity.inventory_location
        inv.remove(entity)
        dest.add(entity)

    def remove(self, entity, run_checks=True):
        if run_checks:
            self.can_remove(entity)
        inv = entity.inventory_location
        inv.remove(entity)
        self.contents.remove(entity)


class EquipRequest(object):

    def __init__(self, handler, entity, gearset=None, gearset_name=None, gearslot=None, gearslot_name=None, layer=None):
        self.handler = handler
        self.equipper = handler.owner
        self.entity = entity
        self.gearset = gearset
        self.gearset_name = gearset_name
        self.gearslot = gearslot
        self.gearslot_name = gearslot_name
        self.layer = layer
        self.process()

    def process(self):
        if not self.gearset:
            if not self.gearset_name:
                self.gearset_name = self.entity.default_gearset
            if not self.gearset_name:
                raise ValueError(f"{self.entity} cannot be equipped: No GearSet to equip it to.")
            self.gearset = self.handler.get_gearset(self.gearset_name)

        if not self.gearslot:
            if not self.gearslot_name:
                self.gearslot_name = self.entity.default_gearslot
            if not self.gearslot_name:
                raise ValueError(f"{self.entity} cannot be equipped: No GearSlot is available for {self.gearset}!")
            self.gearslot = self.gearset.get_gearslot(self.gearslot_name)

        # Remember, layer 0 is a totally viable layer. We can't just check for False here.
        self.layer = self.gearslot.available_layer(self.layer)
        if self.layer is None:
            raise ValueError(f"{self.gearslot} has no available layers!")


class GearHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.gearsets = dict()
        self.contents = set()

    @property
    def equipped(self):
        all = set()
        for inv in self.gearsets.values():
            all += inv.equipped
        return list(all)

    def all(self, gearset_name=None):
        if not gearset_name:
            return list(self.contents)
        else:
            if gearset_name in self.gearsets:
                return self.gearsets[gearset_name].all()
            else:
                return list()

    def get_gearset(self, set_name):
        if (found := self.gearsets.get(set_name, None)):
            return found
        inv_class = class_from_module(settings.SPECIAL_GEARSET_CLASSES.get(set_name, settings.BASE_GEARSET_CLASS))
        new_inv = inv_class(self, set_name)
        self.gearsets[set_name] = new_inv
        return new_inv

    def can_equip(self, entity):
        if entity in self.contents:
            raise ValueError(f"{entity} is already equipped by {self.owner}!")
        if entity not in self.owner.items.contents:
            raise ValueError(f"{self.owner} is not carrying {entity}!")
        entity.inventory_location.can_remove(entity)

    def equip(self, entity, set_name=None, set_slot=None, set_layer=None, run_checks=True):
        if run_checks:
            self.can_equip(entity)
        request = EquipRequest(self, entity, gearset_name=set_name, gearslot_name=set_slot, layer=set_layer)
        if run_checks:
            for aspect in self.owner.aspects.all():
                if not aspect.at_before_equip(entity, request):
                    raise ValueError(f"{aspect} does not allow equipping {entity}!")
        self.owner.items.remove(entity)
        request.gearset.equip(request)
        self.contents.add(entity)

    def can_unequip(self, entity):
        if entity not in self.contents:
            raise ValueError(f"{self.owner} is not using {entity}!")
        old_gear = entity.equip_location
        old_gear.can_unequip(entity)

    def unequip(self, entity, inv_name=None, run_checks=True):
        if run_checks:
            self.can_unequip(entity)
            self.owner.items.can_add(entity, inv_name)
        gear = entity.equip_location
        gear.remove(entity)
        self.contents.remove(entity)
        self.owner.items.add(entity, inv_name, run_checks=False)