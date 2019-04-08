from athanor import AthException


class MudHandler(object):
    """
    The MudHandler is a platform meant to be added via @lazy_property as .properties to Objects.

    Example:
        @lazy_property
        def weight(self):
            return WeightHandler(self)

    These bundle up common operations and systems into flat APIs. This class is abstract and not meant to be used
    by itself.
    """
    category = None

    def __init__(self, owner):
        """
        Set up the Handler and establish shortcuts to its properties.

        Args:
            owner (object): An ObjectDB instance that will hold this Handler.
        """
        # creating some shortcut properties for easy referencing.
        self.owner = owner
        self.attr = owner.attributes
        self.nattr = owner.nattributes

        # Call the sanity checker. This ensures that all objects have the needed base properties!
        self.sanity_check()

        # Fill up the NDB with all of our necessary useful values!
        self.load()

    def sanity_check(self):
        pass

    def load(self):
        pass

    def get(self, attr, default=None):
        """
        Shortcut to the object.attributes.get() API. Fills in category automatically.

        Args:
            attr (str): The key of the Attribute to retrieve.
            default: If the attribute doesn't exist, return this instead.

        Returns:
            Value of Attribute or default. Could be anything.
        """
        return self.attr.get(attr, category=self.category, default=default)

    def add(self, attr, value):
        """
        Shortcut to the object.attributes.add() API. Fills in category automatically.

        Args:
            attr (str): Key of the attribute to set.
            value: Value to set to the Attribute.

        Returns:

        """
        self.attr.add(attr, category=self.category, value=value)

    def has(self, attr):
        """
        Shortcut to checking to see if whether an Attribute exists.

        Args:
            attr (str): Key of the attribute to check.

        Returns:
            existence (bool): Whether the attribute exists.
        """
        return self.attr.has(attr, category=self.category)

    def nget(self, attr):
        return self.nattr.get(attr)

    def nadd(self, attr, value):
        return self.nattr.add(attr, value)


class WeightHandler(MudHandler):
    """
    The WeightHandler is the default implementation of the Weight System for inventories. Its main purpose is to ensure
    that Objects have the proper attributes to interact with the Weight System, and to update .ndb stored values
    as they change throughout gameplay by speaking to the WeightHandlers on other objects.

    This is meant to be accessed as a .weight @lazy_property on Objects. Sub-classes exist below though: use those!
    """
    category = 'weight'

    def sanity_check(self):
        if not self.has('base'):
            self.add('base', value=0)
        if not isinstance(self.get('base'), int):
            self.add('base', value=0)

    def load(self):
        quantity = self.owner.stack.quantity()
        base = self.base()
        total = base * quantity
        equipped = set([i for i in self.owner.contents if i.equipped_by.exists()])
        carried = set(self.owner.contents).difference(equipped)
        carry_weight = sum([i.weight.total() for i in carried])
        equip_weight = sum([i.weight.total() for i in equipped])
        held_weight = carry_weight - equip_weight
        self.nadd('carried', carry_weight)
        self.nadd('held', held_weight)
        self.nadd("equipped", equip_weight)
        self.nadd('total', (base * quantity) + carry_weight)

    def base(self):
        """
        This is what the object would be in its default state, totally empty. An empty sack. A naked human. Whatever.
        This probably won't change. But it can!

        Returns:
            weight (int): The base weight of the Object.
        """
        return self.get('base')

    def base_change(self, modifier):
        """
        Used to alter an object's base weight.

        Args:
            modifier (int): The positive or negative value to add to base weight.
            cascade (bool): Whether to report this change to carrying objects.

        Returns:

        """
        base = self.base()
        self.add('base', value=max(0, int(base + modifier)))
        new_current = self.base() * self.owner.stack.quantity()
        self.total_change(new_current - base)

    def capacity(self):
        """
        The Capacity weight is how much weight this Object CAN CARRY. Not how much it CAN ADD ON or IS CARRYING.
        Note that equipped items are still considered carried.

        Returns:
            weight (int): How much weight the object can carry.

        """
        return self.get('capacity', default=0)

    def capacity_remaining(self):
        """
        This is just capacity - carried weight.

        Returns:
            weight (int): How much weight this object can still hold.
        """
        return self.capacity() - self.carried()

    def total(self):
        """
        The Total Weight is how much this object appears to weigh, in total. It's a combination of the CURRENT weight
        and the CARRIED weight. EQUIPPED weight is not a part of the calculation directly, as it's part of CARRIED
        already.

        Returns:
            weight (int): How much the object effectively weighs if other objects wanted to move it.
        """
        return self.nget('total')

    def total_change(self, modifier):
        """

        Args:
            modifier:

        Returns:

        """
        total = self.total()
        self.nadd('total', value=max(0, int(total + modifier)))
        self.cascade_change(modifier, self.owner.equipped_by.exists())

    def carried(self):
        """
        The Carried weight is how much weight appears to be contained in this object's inventory.

        Returns:
            weight (int): How much weight is carried by this Object.
        """
        return self.nget('carried')

    def carried_change(self, modifier):
        """
        Change the Carried weight for this Object. Best called by .carried_change_signal()

        Args:
            modifier (int): Positive or negative value to change it by.

        Returns:

        """
        carried = self.carried()
        self.nadd('carried', value=max(0, int(carried + modifier)))
        multiplied = max(0, int(round(modifier * self.storage_multiplier())))
        self.total_change(multiplied)

    def storage_multiplier(self):
        """
        Some Objects might have a Storage Multiplier. While Objects still have a maximum capacity, this governs how
        heavy the resulting Object will SEEM to be for other things picking it up. IE: A Bag of Holding might be
        able to contain 50 units of gear, but if the storage_multiplier is 0, that's 0 units in your inventory. Handy!

        The system does not actually allow non-integer weight values. It will round naturally up or down on whatever
        the result is. If you want fine control, maybe make it so that 1000 weight units is displayed as 1 kilogram.

        Returns:
            multiplier (float): A number between 0.0 and I dunno, 5.0 or more. 0.0 for no weight, 1.0 for normal weight,
                5.0 for 5x weight...
        """
        return self.get('storage_multiplier')

    def storage_multiplier_change(self):
        """
        Gonna get back to this.

        Returns:

        """
        pass

    def equipped(self):
        """
        The Equipped weight is how much weight is equipped by this object.

        Returns:
            weight (int): How much weight is equipped by this Object.
        """
        return self.nget('equipped')

    def equipped_change(self, modifier):
        equipped = self.equipped()
        self.nadd('equipped', value=max(0, int(equipped + modifier)))

    def held(self):
        """
        The Held weight is how much is specifically held in your inventory. IE: Items not equipped.

        Returns:
            weight (int): How much weight is carried as inventory items.
        """
        return self.nget('held')

    def can_receive_item(self, item):
        if not item.total_real() <= self.capacity() - self.carried():
            raise AthException("weight")
        return True

    def register_item(self, item):
        self.carried_change(item.weight.total())

    def unregister_item(self, item):
        self.carried_change(item.weight.total() * -1)

    def cascade_change(self, modifier, equipped=False):
        """
        The one and ONLY pathway for a contained item to report that its weight has changed to all carrying items in its
        carry hierarchy. This processes relevant changes and then calls the object carrying THIS one, if possible.

        Args:
            modifier (int): The plus or minus of the change. This is in simulated weight after applying the modifiers.
            equipped (bool): If true, the calling item determined that it was equipped by this one and that should
                be updated.

        Returns:

        """
        if self.owner.location and hasattr(self.owner.location, 'weight'):
            if equipped:
                self.owner.location.weight.equipped_change(modifier)
            self.owner.location.weight.total_change(modifier)


class VolumeHandler(MudHandler):
    category = 'volume'

    def sanity_check(self):
        if not self.has('base'):
            self.add('base', value=0)
        if not isinstance(self.get('base'), int):
            self.add('base', value=0)

    def base(self):
        """
        This is what the object would be in its default state. This probably won't change. But it can!

        Returns:
            volume (int): The base volume of the Object.
        """
        return self.get('base')

    def base_change(self, modifier):
        """
        Used to alter an object's base volume.

        Args:
            modifier (int): The positive or negative value to add to base volume.

        Returns:

        """
        base = self.base()
        self.add('base', value=max(0, int(base + modifier)))

    def capacity(self):
        """
        The Capacity volume is how much volume this Object CAN CARRY. Not how much it CAN ADD ON or IS CARRYING.
        Note that equipped items are still considered carried.

        Returns:
            volume (int): How much weight the object can carry.

        """
        return self.get('capacity', default=0)

    def total(self):
        """
        The Total Volume is this object's current, final size, used by other objects to interact with it.
        This really only changes if something MAKES it change...

        Returns:
            volume (int): How large the object effectively is if other objects wanted to move it.
        """
        return self.nget('total')

    def total_change(self, modifier):
        """

        Args:
            modifier:

        Returns:

        """
        total = self.total()
        self.nadd('total', value=max(0, int(total + modifier)))
        self.cascade_change(modifier, self.owner.equipped_by.exists())

    def carried(self):
        """
        The Carried volume is how much of this container's capacity has been consumed.

        Returns:
            volume (int): How much volume is carried by this Object.
        """
        return self.nget('carried')

    def carried_change(self, modifier):
        """
        Change the Carried volume for this Object.

        Args:
            modifier (int): Positive or negative value to change it by.

        Returns:

        """
        carried = self.carried()
        self.nadd('carried', value=max(0, int(carried + modifier)))

    def equipped(self):
        """
        The Equipped volume is how much STUFF is equipped by this object.

        Returns:
            volume (int): How much stuff is equipped by this Object.
        """
        return self.nget('equipped')

    def equipped_change(self, modifier):
        equipped = self.equipped()
        self.nadd('equipped', value=max(0, int(equipped + modifier)))

    def can_receive_item(self, item):
        if not item.total_real() <= self.capacity() - self.carried():
            raise AthException("weight")
        return True

    def register_item(self, item):
        self.carried_change(item.volume.total())

    def unregister_item(self, item):
        self.carried_change(item.volume.total() * -1)

    def cascade_change(self, modifier, equipped=False):
        """
        The one and ONLY pathway for a contained item to report that its weight has changed to all carrying items in its
        carry hierarchy. This processes relevant changes and then calls the object carrying THIS one, if possible.

        Args:
            modifier (int): The plus or minus of the change. This is in simulated weight after applying the modifiers.
            equipped (bool): If true, the calling item determined that it was equipped by this one and that should
                be updated.

        Returns:

        """
        if self.owner.location and hasattr(self.owner.location, 'volume'):
            if equipped:
                self.owner.location.volume.equipped_change(modifier)


class StackHandler(MudHandler):
    category = "stackable"

    def sanity_check(self):
        if not self.quantity():
            self.add('quantity', 1)

    def quantity(self):
        return self.get('quantity')

    def quantity_change(self, modifier, no_signal=False):
        if not self.is_stack():
            raise AthException('not_stack')
        quantity = self.quantity()
        if modifier >= quantity:
            self.owner.safe_delete()
            return
        if not no_signal:
            weight_modify = modifier * self.owner.weight.base()
            volume_modify = modifier * self.owner.volume.base()
            self.owner.weight.carried_change(weight_modify)
            self.owner.volume.carried_change(volume_modify)
        self.add('quantity', value=quantity + modifier)

    def is_stack(self):
        return bool(self.get('is_stack'))

    def can(self, item):
        if not (self.is_stack() and item.stack.is_stack()):
            return False

    def can_stack(self):
        return self.attributes.get('can_stack', category='stackable', default=False)

    def can_split(self, quantity=1):
        if quantity < 1:
            raise AthException('invalid_quantity')
        if not self.is_stack():
            raise AthException("not_stackable")
        if not self.quantity() > quantity:
            raise AthException("stack_lesser")
        return True

    def split(self, quantity=1, splitter=None, destination=None):
        if not splitter:
            splitter = self.owner
        if not destination:
            destination = self.owner
        created = False
        try:
            self.can_split(quantity)
            new_stack = self.owner.copy()
            created = True
            new_stack.stack.quantity(quantity, no_signal=True)
            if destination != self:
                destination.object_can_receive(new_stack)
        except AthException as e:
            if created:
                new_stack.delete()
            return False
        self.quantity_change(quantity * -1)
        if destination != self:
            new_stack.move_to(destination)
        else:
            self.owner.items.receive(new_stack, method='stack_split')
        return True

    def can_merge(self, item, no_exception=False):
        if not self.can_stack() or not item.stack.can_stack():
            if no_exception:
                return False
            raise AthException("not_stackable")
        if not self.owner.tags.get(category='from_prototype') == item.tags.get(category='from_prototype'):
            if no_exception:
                return False
            raise AthException('unmatched_stack')
        return True

    def merge(self, item, no_check=False):
        if not no_check:
            self.can_merge(item)
        self.quantity_change(item.stack.quantity(), no_signal=True)
        item.safe_delete(reason='stack_merge')

    def stack_all(self, item):
        if not self.is_stack():
            raise AthException("not_stackable")
        prototype = item.tags.get(category='from_prototype')
        for candidate in [c for c in self.owner.items.prototype_single_groups[prototype] if
                          c.stack.can_merge(self.owner, no_exception=True)]:
            self.merge(candidate)


class _HasPrototypes(object):

    def ready_prototypes(self):
        self.prototype_single_groups = dict()
        self.prototype_multi_groups = dict()
        self.prototypes_total_groups = dict()
        self.prototypes_none = set()

    def register_prototypes(self, item):
        prototypes = item.tags.get(category='from_prototype', return_tagobj=True, return_list=True)

        # Total Groups is used for the 'holding prototype' checks.
        for p in prototypes:
            if p.key not in self.prototypes_total_groups:
                self.prototypes_total_groups[p.key] = set(item, )
            else:
                self.prototypes_total_groups[p.key].add(item)

        # The None group is used for aiding with display purposes.
        if len(prototypes) == 0:
            self.prototypes_none.add(item)
            return

        # The Single group is also used for aiding with displays.
        if len(prototypes) == 1:
            prot = prototypes[0]
            if prot.key not in self.prototypes_single_groups:
                self.prototypes_single_groups[prot.key] = set(item,)
            else:
                self.prototypes_single_groups[prot.key].add(item)
            return

        # And so is the Multi group.
        if len(prototypes) > 1:
            for p in prototypes:
                if p.key not in self.prototypes_multi_groups:
                    self.prototypes_multi_groups[p.key] = set(item, )
                else:
                    self.prototypes_multi_groups[p.key].add(item)

    def unregister_prototypes(self, item):
        prototypes = item.tags.get(category='from_prototype', return_tagobj=True, return_list=True)

        # Total Groups is used for the 'holding prototype' checks.
        for p in prototypes:
            if p.key in self.prototypes_total_groups:
                self.prototypes_total_groups[p.key].remove(item)
                if not self.prototypes_total_groups[p.key]:
                    del self.prototypes_total_groups[p.key]

        # The None group is used for aiding with display purposes.
        if len(prototypes) == 0:
            self.prototypes_none.remove(item)
            return

        # The Single group is also used for aiding with displays.
        if len(prototypes) == 1:
            p = prototypes[0]
            if p.key in self.prototypes_single_groups:
                self.prototypes_single_groups[p.key].remove(item)
                if not self.prototypes_single_groups[p.key]:
                    del self.prototypes_single_groups[p.key]
            return

        # And so is the Multi group.
        if len(prototypes) > 1:
            if p.key in self.prototypes_multi_groups:
                self.prototypes_multi_groups[p.key].remove(item)
                if not self.prototypes_multi_groups[p.key]:
                    del self.prototypes_multi_groups[p.key]


class InventoryHandler(MudHandler, _HasPrototypes):
    category = "inventory"

    def sanity_check(self):
        pass

    def load(self):
        self.ready_prototypes()
        equipped = {e.item for e in self.owner.equipped.all()}
        self.items = {i for i in self.owner.contents if i not in equipped}
        for i in self.items:
            self.register_prototypes(i)

    def receive(self, item, method=None, source=None):
        pass

    def receive_can(self, item, method=None, source=None):
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

    def release(self, item, method=None, destination=None):
        pass

    def release_can(self, item, method=None, destination=None):
        pass

    def item_display(self):
        pass


class EquipHandler(MudHandler, _HasPrototypes):
    category = 'equip'

    def sanity_check(self):
        pass

    def load(self):
        self.ready_prototypes()
        self.sorted_slots = sorted([i for i in self.owner.attributes.get(category='equipslot', return_list=True, return_obj=True) if i],
                                   key=lambda r: r.value[3])
        self.slots_dict = {r.key: list() for r in self.sorted_slots}
        self.slot_types_dict = {}
        self.slot_layers_dict = {r.key: r.value[2] for r in self.sorted_slots}
        for r in self.sorted_slots:
            if r.value[0] not in self.slot_types_dict:
                self.slot_types_dict[r.value[0]] = list()
            self.slot_types_dict[r.value[0]].append(r.key)

        self.equipped = {e.item for e in self.owner.equipped.all()}
        for e in self.equipped:
            self.register_prototypes(e)
        self.tabs = {d.key: d.value for d in self.owner.attributes.get(category='equiptab', return_list=True, return_obj=True) if d}


    def add(self, item, slot, layer=0, equipper=None, equip_verb='equip', **kwargs):
        if equipper is None:
            equipper = self.owner
        transfer = False
        try:
            if item.location != self:
                transfer = True
                item.object_can_move(equipper, **kwargs)
                self.owner.inventory.receive_can(item, **kwargs)
            slot_key = self.find_slot(item, slot, layer, equipper, **kwargs)
            self.owner.at_before_equip_item(item, slot_key, layer, equipper, **kwargs)
            item.owner.at_before_equipped(equipper, slot_key, layer, **kwargs)
        except AthException as e:
            equipper.print_equip_error(str(e), item, slot, layer, equip_verb, **kwargs)
            return False
        if transfer:
            item.move_to(self.owner, quiet=True)
        from athanor_mudbase.models import EquipSlotType
        slot_type, created = EquipSlotType.objects.get_or_create(key=slot_key)
        self.owner.equipped.create(slot=slot_type, layer=layer, item=item)
        self.owner.weight.equipped_changed(item.weight.total())
        self.owner.weight.held_changed(item.weight.total() * -1)
        self.owner.volume.equipped_change(item.volume_current())
        self.owner.at_after_equip_item(item, slot_key, layer, equipper, **kwargs)
        item.owner.at_after_equipped(equipper, slot_key, layer, **kwargs)
        item.owner.apply_equip_effects(equipper, slot_key, layer, **kwargs)
        return True

    def add_can(self, item, slot, layer=0, equipper=None, **kwargs):
        if equipper is None:
            equipper = self.owner
        if slot not in self.slot_types_dict:
            raise AthException("slots_not_exist")
        tabs = item.equip.tabs()
        if slot not in tabs:
            raise AthException('tab_not_exist')
        item_uses_layer = tabs[slot]
        if layer != item_uses_layer:
            raise AthException('tab_inapplicable_layer')
        # Note: k.key should be 'hold_1' here, and I have proven that it is.
        for s in self.slot_types_dict[slot]:
            if layer not in s.value[2]:
                continue
            if not self.owner.equipped.filter(slot__key=s.key, layer=layer).exists():
                return s.key
        raise AthException("slot_occupied")

    def remove(self, item, remover=None, destination=None, remove_verb='remove', **kwargs):
        force = kwargs.get('force', False)

        if remover is None:
            remover = self
        if destination is None:
            destination = self
        transfer = False
        if item.location != destination:
            transfer = True
        try:
            self.remove_can(item)
            if transfer:
                item.object_can_move(remover, **kwargs)
                destination.object_can_receive(item, **kwargs)
            self.at_before_unequip_item(item, remover, **kwargs)
            item.at_before_unequipped(remover, **kwargs)
        except AthException as e:
            if not force:
                remover.print_unequip_error(str(e), item, remove_verb, **kwargs)
                return False
        item.equipped_by.all().delete()
        item.remove_equip_effects(self)
        self.owner.weight.equipped_change(item.weight.total() * -1)
        self.owner.weight.held_changed(item.weight.total())
        self.owner.volume.equipped_change(item.weight.total() * -1)
        if transfer:
            item.move_to(destination, quiet=True)
        return True

    def remove_can(self, item):
        if not self.equipped.filter(item=item).exists():
            raise AthException('not_equipped')

    def equip_display(self, viewer=None):
        message = list()
        if not viewer:
            viewer = self
        slots = self.slots()
        for s in slots:
            for l in self.equipped.filter(slot__key=s.key).order_by('layer'):
                message.append('<%s> (Layer %s): %s' % (s.value[1], l.layer, l.item))
        viewer.msg('\n'.join(str(l) for l in message))


class TemplateHandler(MudHandler):
    template_keys = dict()
    template_categories = dict()
    template_tags = dict()
    template_loaded = False

    def load_templates(self):
        """
        This loads up the Template data to the Class itself. The template candidates are referenced on the Typeclass.

        Returns:
            None
        """
        candidates = self.owner.template_candidates
        for c in candidates:
            self.template_keys[c.key] = c
            if c.category is not None:
                if c.category not in self.template_categories:
                    self.template_categories[c.category] = list()
                self.template_categories[c.category].append(c)
            for t in c.tags:
                if t not in self.template_tags:
                    self.template_tags[t] = list()
                self.template_tags[t].append(t)
        self.template_loaded = True

    def load(self):
        if not self.template_loaded:
            self.load_templates()
        self.slots_dict = {i.key: i for i in self.owner.attributes.get(category='templateslot',
                                                           return_list=True, return_obj=True) if i}
        save_data = [s for s in self.attr.get(category='templatesave', return_obj=True, return_list=True) if s]
        self.templates = dict()
        for s in save_data:
            if s.value in self.template_keys and s.key in self.slots_dict:
                self.templates[s.key] = self.template_keys[s.value](self)

