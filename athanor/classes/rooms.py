"""
Room

Rooms are simple containers that has no location of their own.

"""
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
        message.append(session.ath['render'].header(self.key))
        message.append(self.db.desc)
        chars = self.online_characters(viewer=viewer)
        if chars:
            message.append(session.ath['render'].subheader("Characters"))
            message.append(self.format_character_list(chars, session))
        if self.exits:
            message.append(session.ath['render'].subheader("Exits"))
            message.append(self.format_exit_list(self.exits, session))
        message.append(session.ath['render'].footer())
        return "\n".join([unicode(line) for line in message])

    def online_characters(self, viewer=None):
        if viewer:
            return [char for char in characters() if char.location and self.can_see(viewer, char)]
        return [char for char in characters() if char.location == self]

    def can_see(self, viewer, character):
        if viewer.ath['core'].is_admin():
            return True
        return not character.ath['core'].dark

    def format_character_list(self, characters, session):
        columns = (('Name', 0, 'l'), ('Description', 0, 'l'))
        char_table = session.ath['render'].table(columns, border=None)
        for char in characters:
            char_table.add_row(char.key, char.db.shortdesc)
        return char_table

    def format_exit_list(self, exits, session):
        exit_table = []
        for exit in exits:
            exit_table.append(exit.format_output(session))
        return tabular_table(exit_table, field_width=36, line_length=session.ath['render'].width(), truncate_elements=False)

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
