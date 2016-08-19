"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from __future__ import unicode_literals

from evennia import DefaultCharacter
from evennia.utils.utils import time_format, lazy_property
from evennia.utils.ansi import ANSIString
from athanor.library import utcnow, mxp_send

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
        from athanor.core.models import CharacterSetting
        CharacterSetting.objects.get_or_create(character=self)
        self.character_settings.update_last_played()

    def at_post_unpuppet(self, player, session=None):
        super(Character, self).at_post_unpuppet(player, session)
        self.character_settings.update_last_played()
        if self.sessions:
            return
        self.channel_gags.db_channel.clear()
        if self.db._owner.db._watch_mute:
            return
        for player in [play.db_player for play in self.on_watch.all() if not play.db_player.db._watch_mute]:
            player.sys_msg('%s has disconnected.' % self, sys_name='WATCH')

    def at_post_puppet(self):
        super(Character, self).at_post_puppet()
        self.character_settings.update_last_played()
        self.puppet_logs.create(player=self.player)
        if len(self.sessions.all()) != 1 and not self.db._owner.db._watch_hide:
            for player in [play.db_player for play in self.on_watch.all() if not play.db_player.db._watch_mute]:
                player.sys_msg('%s has connected.' % self, sys_name='WATCH')

    def search_character(self, search_name=None):
        """
        Wrapper method for .search() for Characters only. Used by most Athanor code.

        Args:
            search_name (string) - Name to search for.

        Returns:
            ObjectDB instance.

        Raises:
            ValueError: If character cannot be found.

        """
        if not search_name:
            raise ValueError("Character name field empty.")

        # First, collect all possible character candidates.
        candidates = Character.objects.filter_family()

        # First we'll run an Exact check.:
        search_results = self.search(search_name, exact=True, use_nicks=True, candidates=candidates, quiet=True)

        # Did that not work? Next we'll try the online match if it's set!
        if not search_results:
            from athanor.library import connected_characters
            search_results = self.search(search_name, exact=False, use_nicks=True, candidates=connected_characters(),
                                         quiet=True)

        # We found NOBODY? Then error!
        if not search_results:
            raise ValueError("Character '%s' not found." % search_name)

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

    def last_played(self, update=False):
        if update:
            self.db._last_played = utcnow()
        return self.db._last_played

    def off_or_idle_time(self, viewer):
        idle = self.idle_time
        if idle is None or not viewer.can_see(self):
            return '|XOff|n'
        return time_format(idle, style=1)

    def off_or_conn_time(self, viewer):
        conn = self.connection_time
        if conn is None or not viewer.can_see(self):
            return '|XOff|n'
        return time_format(conn, style=1)

    def last_or_idle_time(self, viewer):
        idle = self.idle_time
        last = self.last_played()
        if not idle or not viewer.can_see(self):
            return viewer.display_local_time(date=last, format='%b %d')
        return time_format(idle, style=1)

    def last_or_conn_time(self, viewer):
        conn = self.connection_time
        last = self.last_played()
        if not conn or not viewer.can_see(self):
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
        tz = self.settings.get('system_timezone')
        my_time = date.astimezone(tz)
        return my_time.strftime(format)

    def sys_msg(self, message, sys_name='SYSTEM', error=False):
        if error:
            message = '{rERROR:{n %s' % message
        alert = '{%s-=<{n{%s%s{n{%s>=-{n ' % (self.settings.get('msgborder_color'), self.settings.get('msgtext_color'),
                                            sys_name.upper(), self.settings.get('msgborder_color'))
        send_string = alert + message
        self.msg(unicode(ANSIString(send_string)))

    def character_slot_value(self, update=None):
        if update is not None:
            try:
                new_value = int(update)
            except ValueError:
                raise ValueError("Character slots must be non-negative integers.")
            if new_value < 0:
                raise ValueError("Character slots must be non-negative integers.")
            self.db._slot_value = new_value
            self.sys_msg("This Character is now worth %i Character Slots." % new_value)
        return int(self.db._slot_value)

    def mxp_name(self, commands=None):
        if not commands:
            commands = ['+finger']
        send_commands = '|'.join(['%s %s' % (command, self.key) for command in commands])
        return mxp_send(text=self.key, command=send_commands)

    @lazy_property
    def owner(self):
        return self.character_settings.player

    @lazy_property
    def player_settings(self):
        return self.owner.player_settings

    @property
    def screen_width(self):
        width_list = [session.get_client_size()[0] for session in self.sessions.all()]
        return min(width_list) or 78