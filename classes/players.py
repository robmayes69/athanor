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


from evennia import DefaultPlayer, DefaultGuest

from evennia.utils.utils import lazy_property, is_iter
from evennia.utils.ansi import ANSIString
from athanor.utils.handlers.player import PlayerWeb, PlayerTime, PlayerAccount, PlayerRender, ColorHandler
from athanor.core.config import PlayerSettings

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
    @lazy_property
    def config(self):
        return PlayerSettings(self)

    @lazy_property
    def web(self):
        return PlayerWeb(self)

    @lazy_property
    def account(self):
        return PlayerAccount(self)

    @lazy_property
    def time(self):
        return PlayerTime(self)

    @lazy_property
    def render(self):
        return PlayerRender(self)

    @lazy_property
    def colors(self):
        return ColorHandler(self)

    def _send_to_connect_channel(self, message):
        return

    def at_player_creation(self):
        super(Player, self).at_player_creation()

        # All Players need a Settings entry!
        settings = self.config

    def at_post_login(self, session=None):
        super(Player, self).at_post_login(session)

        if len(self.sessions.all()) == 1:
            self.at_true_login(session)

        #Update webclient data...
        if session:
            if session.ndb.gui:
                session.msg(login_player=((), {'data': self.web.login_serialize()}))


    def at_true_login(self, session=None):
        self.config.update_last_played()

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

    def sys_msg(self, message, sys_name='SYSTEM', error=False):
        if error:
            message = '{rERROR:{n %s' % message
        settings = self.config
        alert = '{%s-=<{n{%s%s{n{%s>=-{n ' % (settings['msgborder_color'], settings['msgtext_color'],
                                            sys_name.upper(), settings['msgborder_color'])
        send_string = alert + '(Account) ' + message
        self.msg(unicode(ANSIString(send_string)))

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
            self.render.render_login(session)



class Guest(DefaultGuest, Player):
    """
    This class is used for guest logins. Unlike Players, Guests and their
    characters are deleted after disconnection.
    """
    pass
