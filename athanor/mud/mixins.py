from evennia import DefaultObject, DefaultRoom, DefaultCharacter
from evennia.utils import lazy_property
from athanor import AthException
from athanor.characters.handlers import WeightHandler, VolumeHandler, StackHandler, InventoryHandler, EquipHandler
from athanor.characters.handlers import TemplateHandler


class HasInventory(DefaultObject):

    template_candidates = []

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

    @lazy_property
    def template(self):
        return TemplateHandler(self)

    def at_object_leave(self, moved_obj, destination, **kwargs):
        self.items.release(moved_obj, method=kwargs.get('method', None), destination=destination)

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        self.items.receive(moved_obj, method=kwargs.get('method', None), source=source_location)

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

    def safe_delete(self):
        pass


class MudItem(HasInventory):
    pass


class MudRoom(DefaultRoom, HasInventory):
    pass


class MudZone(DefaultRoom, HasInventory):
    pass


class MudCharacter(DefaultCharacter, HasInventory):
    pass
