"""
Room

Rooms are simple containers that has no location of their own.

"""
from __future__ import unicode_literals
from evennia import DefaultRoom
from athanor.utils.text import tabular_table

class BaseRoom(DefaultRoom):
    """
    This class is a placeholder meant to represent deleted rooms. It implements the main room logic, but should
    not be used for new rooms.
    """
    style = 'rooms'

    def return_appearance(self, viewer):
        message = list()
        message.append(viewer.styles.header(self.key, style=self.style))
        message.append(self.db.desc)
        chars = self.online_characters(viewer=viewer)
        if chars:
            message.append(viewer.styles.subheader("Characters", style=self.style))
            message.append(self.format_character_list(chars, viewer))
        if self.exits:
            message.append(viewer.styles.subheader("Exits", style=self.style))
            message.append(self.format_exit_list(self.exits, viewer))
        message.append(viewer.styles.footer(style=self.style))
        return "\n".join([unicode(line) for line in message])

    def list_characters(self):
        return sorted([char for char in self.contents if hasattr(char, 'ath')],
                      key=lambda char: char.key.lower())

    def online_characters(self, viewer=None):
        characters = [char for char in self.list_characters() if char.sessions]
        if viewer:
            characters = [char for char in characters if viewer.ath['system'].can_see(char)]
        return characters

    def format_character_list(self, characters, viewer):
        char_table = viewer.styles.make_table(["Name", "Description"], border=None, width=[20, 40], style=self.style)
        for char in characters:
            char_table.add_row(char.key, char.db.shortdesc)
        return char_table

    def format_exit_list(self, exits, caller):
        exit_table = []
        for exit in exits:
            exit_table.append(exit.format_output(caller))
        return tabular_table(exit_table, field_width=36, line_length=78, truncate_elements=False)

    def format_roomlist(self):
        return "|C%s|n |x%s|n" % (self.dbref.ljust(6), self.key)


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