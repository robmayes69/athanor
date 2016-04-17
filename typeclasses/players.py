"""
Player

The Player represents the game "account" and each login has only one
Player object. A Player is what chats on default channels but has no
other in-game-world existance. Rather the Player puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest players are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the committment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from __future__ import unicode_literals

import time
from django.conf import settings
from evennia import DefaultPlayer, DefaultGuest
from evennia import utils
from evennia.utils.utils import time_format, lazy_property
from evennia.utils.ansi import ANSIString
from evennia.utils.utils import is_iter
from evennia.utils.evmenu import get_input
from commands.library import utcnow, sanitize_string, header, make_table, make_column_table, subheader
from world.player_settings import SettingHandler

class Player(DefaultPlayer):
    """
    This class describes the actual OOC player (i.e. the user connecting
    to the MUD). It does NOT have visual appearance in the game world (that
    is handled by the character which is connected to this). Comm channels
    are attended/joined using this object.

    It can be useful e.g. for storing configuration options for your game, but
    should generally not hold any character-related info (that's best handled
    on the character level).

    Can be set using BASE_PLAYER_TYPECLASS.


    * available properties

     key (string) - name of player
     name (string)- wrapper for user.username
     aliases (list of strings) - aliases to the object. Will be saved to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     user (User, read-only) - django User authorization object
     obj (Object) - game object controlled by player. 'character' can also be used.
     sessions (list of Sessions) - sessions connected to this player
     is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create a database entry when storing data
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().

    * Helper methods

     msg(text=None, **kwargs)
     swap_character(new_character, delete_old_character=False)
     execute_cmd(raw_string, sessid=None)
     search(ostring, global_search=False, attribute_name=None, use_nicks=False, location=None, ignore_errors=False, player=False)
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hook methods (when re-implementation, remember methods need to have self as first arg)

     basetype_setup()
     at_player_creation()

     - note that the following hooks are also found on Objects and are
       usually handled on the character level:

     at_init()
     at_cmdset_get(**kwargs)
     at_first_login()
     at_post_login(sessid=None)
     at_disconnect()
     at_message_receive()
     at_message_send()
     at_server_reload()
     at_server_shutdown()

    """
    def _send_to_connect_channel(self, message):
        return

    def at_player_creation(self):
        super(Player, self).at_player_creation()

        # Initialize the playable characters list.
        if not self.db._playable_characters:
            self.db._playable_characters = []

        # All Players need an Actor and WatchFor entry!
        from world.database.communications.models import PlayerStub, WatchFor
        PlayerStub.objects.get_or_create(player=self, key=self.key)
        WatchFor.objects.get_or_create(player=self)

    def at_post_login(self, session=None):
        super(Player, self).at_post_login(session)
        self.last_played(update=True)

    def at_failed_login(self, session=None):
        super(Player, self).at_failed_login(session)
        self.sys_msg('WARNING: Detected a failed login.')

    def is_admin(self):
        return self.locks.check_lockstring(self, "dummy:perm(Wizards)")

    def get_all_puppets(self):
        """
        Replaces the default method. Only difference is that it sorts them!
        """
        return sorted(super(Player, self).get_all_puppets(), key=lambda char: char.key)

    def get_all_characters(self):
        """
        Returns a list of all valid playable characters.
        """
        return [char for char in self.db._playable_characters if char]

    def bind_character(self, character):
        """
        This method is used to attach a character to a player.

        Args:
            character (objectdb): The character being bound.
        """

        #First we'll unbind any existing owner.
        old_player = character.db._owner
        if old_player:
            old_player.unbind_character(character)

        #Now set the new owner.
        character.db._owner = self
        character.reset_puppet_locks(self)

        #Lastly, add the new character to our playable characters.
        characters = self.get_all_characters()
        characters.append(character)
        self.db._playable_characters = sorted(list(set(characters)), key=lambda char: char.key)

    def unbind_character(self, character):
        characters = self.get_all_characters()
        characters.remove(character)
        self.db._playable_characters = sorted(list(set(characters)), key=lambda char: char.key)

    def delete(self, *args, **kwargs):
        self.actor.update_name(self.key)
        super(Player, self).delete(*args, **kwargs)

    def display_local_time(self, date=None, format=None):
        if not format:
            format = '%b %d %I:%M%p %Z'
        if not date:
            date = utcnow()
        tz = self.settings.get('timezone')
        time = date.astimezone(tz)
        return time.strftime(format)

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

    def last_played(self, update=False):
        if update:
            self.db._last_played = utcnow()
        return self.db._last_played

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

    def sys_msg(self, message, sys_name='SYSTEM', error=False):
        if error:
            message = '{rERROR:{n %s' % message
        alert = '{%s-=<{n{%s%s{n{%s>=-{n ' % (self.settings.get('msgborder_color'), self.settings.get('msgtext_color'),
                                            sys_name.upper(), self.settings.get('msgborder_color'))
        send_string = alert + '(Account) ' + message
        self.msg(unicode(ANSIString(send_string)))

    def can_see(self, target):
        if self.is_admin():
            return True
        if target.is_dark() or target.is_hidden():
            return False
        return True

    def extra_character_slots(self, update=None):
        """
        This method is used to set and/or retrieve how many Extra Character Slots a Player has.

        Args:
            update (str or int): If provided, sets the character's available extra slots.

        Raises:
            AthanorError: If the update argument cannot be converted to a non-negative integer.

        Returns:
            int
        """
        if not self.db._character_slots:
            self.db._character_slots = 0
        if update is not None:
            try:
                new_value = int(update)
            except ValueError:
                raise ValueError("Character slots must be non-negative integers.")
            if new_value < 0:
                raise ValueError("Character slots must be non-negative integers.")
            self.db._character_slots = new_value
            self.sys_msg("You now have %i Extra Character Slots." % new_value)
        return int(self.db._character_slots)

    def max_character_slots(self):
        return settings.MAX_NR_CHARACTERS + self.extra_character_slots()

    def used_character_slots(self):
        return sum([char.character_slot_value() for char in self.get_all_characters()])

    @lazy_property
    def settings(self):
        return SettingHandler(self)

    @property
    def screen_width(self):
        width_list = list()
        for session in self.sessions.all():
            width_list += session.protocol_flags['SCREENWIDTH'].values()
        return min(width_list) or 78

    def at_look(self, target=None, session=None):
        """
        Called when this object executes a look. It allows to customize
        just what this means.

        Args:
            target (Object or list, optional): An object or a list
                objects to inspect.
            session (Session, optional): The session doing this look.

        Returns:
            look_string (str): A prepared look string, ready to send
                off to any recipient (usually to ourselves)

        """

        if target and not is_iter(target):
            # single target - just show it
            return target.return_appearance()
        else:
            characters = list(target)
            message = list()
            message.append(header("%s: Account Management" % settings.SERVERNAME))
            message.append(self.at_look_info_section())
            message += self.at_look_session_menu()
            message.append(subheader('Commands'))
            command_column = make_column_table()
            command_text = list()
            command_text.append(unicode(ANSIString(" {whelp{n - more commands")))
            if self.db._reset_username:
                command_text.append(" {w@username <name>{n - Set your username!")
            if self.db._reset_email or self.email == 'dummy@dummy.com':
                command_text.append(" {w@email <address>{n - Set your email!")
            if self.db._was_lost:
                command_text.append(" {w@penn <character>=<password>{n - Link an imported PennMUSH character.")
            command_text.append(" {w@charcreate <name> [=description]{n - create new character")
            command_text.append(" {w@ic <character>{n - enter the game ({w@ooc{n to get back here)")
            command_column.add_row("\n".join(command_text), width=78)
            message.append(command_column)
            message += self.at_look_character_menu()

            message.append(subheader('Open Char Slots: %s/%s' % (
                self.max_character_slots() - len(characters), self.max_character_slots())))
            self.msg('\n'.join(unicode(line) for line in message))

    def at_look_info_section(self, viewer=None):
        if not viewer:
            viewer = self
        message = list()
        info_column = make_column_table()
        info_text = list()
        info_text.append(unicode(ANSIString("Account:".rjust(8) + " {g%s{n" % (self.key))))
        email = self.email if self.email != 'dummy@dummy.com' else '<blank>'
        info_text.append(unicode(ANSIString("Email:".rjust(8) + ANSIString(" {g%s{n" % email))))
        info_text.append(unicode(ANSIString("Perms:".rjust(8) + " {g%s{n" % ", ".join(self.permissions.all()))))
        info_column.add_row("\n".join(info_text), width=78)
        message.append(info_column)
        return message

    def at_look_session_menu(self, viewer=None):
        if not viewer:
            viewer = self
        sessions = self.sessions.all()
        message = list()
        message.append(subheader('Sessions', viewer=viewer))
        sesstable = make_table('ID', 'Protocol', 'Address', 'Connected', width=[7, 22, 22, 27], viewer=viewer)
        for session in sessions:
            conn_duration = time.time() - session.conn_time
            sesstable.add_row(session.sessid, session.protocol_key,
                                isinstance(session.address, tuple) and str(session.address[0]) or str(
                                    session.address),
                                 utils.time_format(conn_duration, 0))
        message.append(sesstable)
        # message.append(separator())
        return message

    def at_look_character_menu(self, viewer=None):
        if not viewer:
            viewer = self
        message = list()
        characters = self.get_all_characters()
        message.append(subheader('Characters', viewer=viewer))
        chartable = make_table('ID', 'Name', 'Type', 'Last Login', width=[7, 36, 15, 20], viewer=viewer)
        for character in characters:
            login = character.last_played()
            if login:
                login = self.display_local_time(date=login)
            else:
                login = 'N/A'
            chartable.add_row(character.id, character.key, character.character_type, login)
        message.append(chartable)
        # message.append(separator())
        return message

class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Players, Guests and their
    characters are deleted after disconnection.
    """
    pass
