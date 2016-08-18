"""
Room

Rooms are simple containers that has no location of their own.

"""
from __future__ import unicode_literals
from django.conf import settings
from athanor.typeclasses.characters import Character
from evennia import DefaultRoom
from athanor.library import header, subheader, make_table, tabular_table

class BaseRoom(DefaultRoom):
    """
    This class is a placeholder meant to represent deleted rooms. It implements the main room logic, but should
    not be used for new rooms.
    """

    def return_appearance(self, caller):
        message = []
        message.append(header(self.key, viewer=caller))
        message.append(self.db.desc)
        chars = self.online_characters(viewer=caller)
        if chars:
            message.append(subheader("Characters", viewer=caller))
            message.append(self.format_character_list(chars, caller))
        if self.exits:
            message.append(subheader("Exits", viewer=caller))
            message.append(self.format_exit_list(self.exits, caller))
        message.append(header())
        message2 = []
        for line in message:
            message2.append(unicode(line))
        return "\n".join(message2)

    def list_characters(self):
        return sorted([char for char in self.contents if char.is_typeclass(Character, exact=False)],
                      key=lambda char: char.key.lower())

    def online_characters(self, viewer=None):
        characters = [char for char in self.list_characters() if char.sessions]
        if viewer:
            characters = [char for char in characters if viewer.can_see(char)]
        return characters

    def sys_msg(self, message, sys_name='SYSTEM', error=False, sender=None):
        for char in self.online_characters():
            char.sys_msg(message, sys_name, error=error)

    def format_character_list(self, characters, caller):
        char_table = make_table("Name", "Description", border=None, width=[20, 40])
        for char in characters:
            char_table.add_row(char.key, char.db.shortdesc)
        return char_table

    def format_exit_list(self, exits, caller):
        exit_table = []
        for exit in exits:
            exit_table.append(exit.format_output(caller))
        return tabular_table(exit_table, field_width=36, line_length=78, truncate_elements=False)

    def format_roomlist(self):
        return "{C%s{n {x%s{n" % (self.dbref.ljust(6), self.key)


class Room(BaseRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    pass