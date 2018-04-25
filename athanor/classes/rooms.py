"""
Room

Rooms are simple containers that has no location of their own.

"""
from __future__ import unicode_literals
from evennia import DefaultRoom
from athanor.utils.text import tabular_table
from athanor.utils.online import characters

class BaseRoom(DefaultRoom):
    """
    This class is a placeholder meant to represent deleted rooms. It implements the main room logic, but should
    not be used for new rooms.
    """
    style = 'rooms'

    def return_appearance(self, session, viewer):
        message = list()
        message.append(session.render.header(self.key, style=self.style))
        message.append(self.db.desc)
        chars = self.online_characters(viewer=viewer)
        if chars:
            message.append(session.render.subheader("Characters", style=self.style))
            message.append(self.format_character_list(chars, session))
        if self.exits:
            message.append(session.render.subheader("Exits", style=self.style))
            message.append(self.format_exit_list(self.exits, session))
        message.append(session.render.footer(style=self.style))
        return "\n".join([unicode(line) for line in message])

    def online_characters(self, viewer=None):
        if viewer:
            return [char for char in characters() if char.location == self and viewer.ath['who'].can_see(char)]
        return [char for char in characters() if char.location == self]

    def format_character_list(self, characters, viewer):
        columns = (('Name', 0, 'l'), ('Description', 0, 'l'))
        char_table = viewer.render.table(columns, border=None, style=self.style)
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