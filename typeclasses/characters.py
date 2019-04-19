"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter


class Character(DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on rooms. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the rooms.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """
    def display_name(self, viewer):
        return self.key

    def current_weight(self):
        return sum([t.weight() for t in self.db.body.values() if t]) + self.weight_held()

    def weight_held(self):
        return sum([t.weight() for t in self.db.items])

    def weight_worn(self):
        return sum(i.current_weight() for i in self.db.equip.values())

    def inventory_items(self):
        return [i for i in self.contents if i.db.equip_character is None]

    def current_stance(self):
        pass

    def occupy_seat(self, target):
        pass

    def change_stance(self, new_stance, target=None, force=False):
        if target:
            if new_stance not in target.seat_stances():
                raise ValueError("%s cannot accomodate you!" % target.name(self))
            if target.db.occupant is not None or target.db.occupant != self:
                raise ValueError("%s is currently occupied!" % target.name(self))

    def is_aware(self):
        pass

    def is_asleep(self):
        pass

    def is_resting(self):
        pass

    def can_carry_capacity(self):
        return len(self.inventory_items()) < self.db.item_capacity

    def can_carry_weight(self, target):
        return (self.weight_held() + target.current_weight()) <= self.db.weight_capacity

    def can_be_carried(self):
        return False

    def can_carry(self, target):
        can_be_check = target.can_be_carried()
        capacity_check = self.can_carry_capacity()
        weight_check = self.can_carry_weight(target)
        output = ''
        if not self.can_carry_capacity():
            raise ValueError("You can't carry that many things!")




    def pickup_item(self, target):
        carry_check = self.can_carry(target)

    def put_item(self, item, container):
        pass

    def common_key(self, viewer):
        return self.key


class PlayerCharacter(DefaultCharacter):
    pass


class MobileCharacter(DefaultCharacter):
    """
    This is used for all NPCs.
    """
    pass
