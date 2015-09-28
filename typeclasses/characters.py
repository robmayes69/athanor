"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
import time, pytz
from evennia import DefaultCharacter
from evennia.utils.utils import time_format
from evennia.utils.ansi import ANSIString
from commands.library import AthanorError, utcnow, mxp_send

class Character(DefaultCharacter):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """

    def at_object_creation(self):
        super(Character, self).at_object_creation()
        from world.database.communications.models import ObjectActor
        ObjectActor.objects.create(db_object=self, db_key=self.key)
        self.last_played(update=True)

    def at_post_unpuppet(self, player, sessid=None):
        super(Character, self).at_pre_puppet(player, sessid)
        self.last_played(update=True)

    def at_post_puppet(self):
        super(Character, self).at_post_puppet()
        self.last_played(update=True)

    def search_character(self, search_name):
        """
        Wrapper method for .search() for Characters only. Used by most Athanor code.

        Args:
            search_name (string) - Name to search for.

        Returns:
            ObjectDB instance.

        Raises:
            AthanorError: If character cannot be found.

        """
        # First, collect all possible character candidates.
        candidates = Character.objects.filter_family()

        # First we'll run an Exact check.:
        search_results = self.search(search_name, exact=True, use_nicks=True, candidates=candidates, quiet=True)

        # Did that not work? Next we'll try the online match if it's set!
        if not search_results:
            from commands.library import connected_characters
            search_results = self.search(search_name, exact=False, use_nicks=True, candidates=connected_characters(),
                                         quiet=True)

        # We found NOBODY? Then error!
        if not search_results:
            raise AthanorError("Character '%s' not found." % search_name)

        # We only want to return one result, even if multiple matches were found.
        if isinstance(search_results, list):
            return search_results[0]
        else:
            return search_results

    def reset_puppet_locks(self, player):
        """
        Called by the processes for binding a character to a player.
        """
        self.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" % (self.id, player.id))

    def delete(self):
        self.actor.update_name(self.key)
        super(Character, self).delete()

    @property
    def idle_time(self):
        idle = [session.cmd_last_visible for session in self.sessions]
        if idle:
            return time.time() - float(max(idle))

    @property
    def connection_time(self):
        conn = [session.conn_time for session in self.sessions]
        if conn:
            return time.time() - float(min(conn))

    def is_admin(self):
        return self.locks.check_lockstring(self, "dummy:perm(Wizards)")

    def is_dark(self, value=None):
        """
        Dark characters appear offline except to admin.
        """
        if value is not None:
            self.db._dark = value
            self.sys_msg("You %s DARK." % ('are now' if value else 'are no longer'))
        return self.db._dark

    def is_hidden(self, value=None):
        """
        Hidden characters only appear on the who list to admin.
        """
        if value is not None:
            self.db._hidden = value
            self.sys_msg("You %s HIDDEN." % ('are now' if value else 'are no longer'))
        return self.db._hidden

    def can_see(self, target):
        if self.is_admin():
            return True
        if target.is_dark() or target.is_hidden():
            return False
        return True

    def timezone(self, value=None):
        owner = self.db._owner
        if owner:
            return owner.timezone(value=value)
        else:
            return pytz.UTC

    def last_played(self, update=False):
        if update:
            self.db._last_played = utcnow()
        return self.db._last_played

    def last_or_idle_time(self, viewer):
        idle = self.idle_time
        last = self.last_played()
        if not idle or not viewer.can_see(self):
            tz = viewer.timezone()
            return viewer.display_local_time(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.connection_time
        last = self.last_played()
        if not conn or not viewer.can_see(self):
            tz = viewer.timezone()
            return viewer.display_local_time(date=last, format='%b %d')
        return time_format(conn, style=1)

    def display_local_time(self, date=None, format=None):
        owner = self.db._owner
        if owner:
            return owner.display_local_time(date=date, format=format)
        if not format:
            format = '%b %d %I:%M%p %Z'
        if not date:
            date = utcnow()
        tz = self.timezone()
        time = date.astimezone(tz)
        return time.strftime(format)

    def sys_msg(self, message, sys_name='SYSTEM', error=False):
        alert = sys_name + '>'
        self.msg(unicode(ANSIString(alert + message)))

    def character_slot_value(self, update=None):
        if update is not None:
            try:
                new_value = int(update)
            except ValueError:
                raise AthanorError("Character slots must be non-negative integers.")
            if new_value < 0:
                raise AthanorError("Character slots must be non-negative integers.")
            self.db._slot_value = new_value
            self.sys_msg("This Character is now worth %i Character Slots." % new_value)
        return int(self.db._slot_value)

    def mxp_name(self, commands=None):
        if not commands:
            commands = ['+finger']
        send_commands = '|'.join(['%s %s' % (command, self.key) for command in commands])
        return mxp_send(text=self.key, command=send_commands)