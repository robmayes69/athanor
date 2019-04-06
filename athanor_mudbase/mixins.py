from evennia import DefaultObject, DefaultRoom, DefaultCharacter
from evennia.utils import lazy_property
from athanor import AthException
from athanor_mudbase.mudhandlers import WeightHandler, VolumeHandler, StackHandler, InventoryHandler, EquipHandler


class HasInventory(DefaultObject):

    @lazy_property
    def weight(self):
        return WeightHandler(self)

    @lazy_property
    def volume(self):
        return VolumeHandler(self)

    @lazy_property
    def stack(self):
        return StackHandler(self)

    @lazy_property
    def items(self):
        return InventoryHandler(self)

    @lazy_property
    def equip(self):
        return EquipHandler(self)

    def at_object_leave(self, moved_obj, destination, **kwargs):
        self.weight.unregister_item(moved_obj)
        self.volume.unregister_item(moved_obj)

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        self.weight.register_item(moved_obj)
        self.volume.register_item(moved_obj)

    def object_can_move(self, mover, **kwargs):
        """
        Meant to be used for handling fixed objects. Stuff that just cannot be moved or removed from inventory
        or whatever. Use self.location if in doubt about such rules!
        """
        if self.tags.get('fixed', category='item'):
            raise AthException('fixed')
        return True

    def object_can_receive(self, item, **kwargs):
        if item.location == self:
            raise AthException('already_possessed')
        if not self.weight_can_add(item):
            raise AthException('weight')
        if not self.volume_can_add(item):
            raise AthException('volume')
        contain_tags = set(self.tags.get(category='contain', return_list=True))
        item_types = set(item.tags.get(category='itemtype', return_list=True))
        if contain_tags:
            if not contain_tags.intersection(item_types):
                raise AthException('incompatible_type')
        location = self.location
        while location is not None:
            if location == item:
                raise AthException('recursion')
            location = location.location
        return True

    def at_before_get(self, getter, **kwargs):
        force = kwargs.get('force', False)
        try:
            if self.tags.get(category='character'):
                raise AthException('character')
            self.object_can_move(getter, **kwargs)
            getter.object_can_receive(self)
        except AthException as e:
            # some errors are so dire that force will be disabled.
            if str(e) in ['character', ]:
                force = False
            getter.print_relocate_error(str(e), self, destination=getter, **kwargs)
            if force:
                getter.msg("... but you yoink %s anyways." % self)
                return True
            return False
        return True

    def print_relocate_error(self, error, item, destination=None):
        if not destination:
            destination = self
        self.msg(error)

    def at_before_give(self, giver, getter, **kwargs):
        force = kwargs.get('force', False)
        try:
            self.object_can_move(giver, **kwargs)
            getter.object_can_receive(self)
        except AthException as e:
            if str(e) in ['character', ]:
                force = False
            giver.print_relocate_error(str(e), self, destination=getter, **kwargs)
            if force:
                giver.msg("... but you gift %s to %s anyways." % (self, getter))
                return True
            return False
        return True

    def print_equip_error(self, error, item, slot, layer, equip_verb, **kwargs):
        self.msg(error)

    def at_before_equip_item(self, item, slot_key, layer, equipper, **kwargs):
        pass

    def at_after_equip_item(self, item, slot_key, layer, equipper, **kwargs):
        pass

    def at_before_equipped(self, equipper, slot_key, layer, **kwargs):
        pass

    def at_after_equipped(self, equipper, slot_key, layer, **kwargs):
        pass

    def apply_equip_effects(self, equipper, slot_key, layer, **kwargs):
        pass

    def remove_equip_effects(self, equipper):
        pass

    def at_before_unequip_item(self, item, remover, **kwargs):
        pass

    def at_before_unequipped(self, remover, **kwargs):
        pass

    def print_unequip_error(self, error, item, remove_verb, **kwargs):
        self.msg(error)


class MudItem(HasInventory):
    pass


class MudRoom(DefaultRoom, HasInventory):
    pass


class MudCharacter(DefaultCharacter, HasInventory):
    pass
