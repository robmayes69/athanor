"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from __future__ import unicode_literals

from evennia import DefaultCharacter, create_script
from evennia.utils.utils import lazy_property
from evennia.utils.ansi import ANSIString
from athanor.utils.text import mxp
from athanor.classes.scripts import WhoManager
from athanor.utils.handlers.character import CharacterWeb, CharacterTime, CharacterAccount
from athanor.utils.handlers.character import CharacterChannel
from athanor.core.config import CharacterSettings
from athanor.core.models import CharacterSetting

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

    @property
    def ath_char(self):
        return True

    @lazy_property
    def who(self):
        found = WhoManager.objects.filter_family(db_key='Who Manager').first()
        if found:
            return found
        return create_script(WhoManager, persistent=False, obj=None)

    @lazy_property
    def web(self):
        return CharacterWeb(self)

    @lazy_property
    def time(self):
        return CharacterTime(self)

    @lazy_property
    def config(self):
        return CharacterSettings(self)

    @lazy_property
    def account(self):
        return CharacterAccount(self)

    @lazy_property
    def channels(self):
        return CharacterChannel(self)

    def at_post_unpuppet(self, player, session=None):
        super(Character, self).at_post_unpuppet(player, session)
        if session:
            session.msg(character_clear=((), {}))
        if not self.sessions.get():
            self.at_true_logout(player, session)

    def at_true_logout(self, player, session=None):
        """
        A sub-hook of at_post_unpuppet for events that process only when all connected sessions disconnect.
        """
        self.config.update_last_played()
        self.who.rem(self)

    def at_true_login(self):
        """
        This is called by at_post_puppet when a character with no previous sessions is puppeted.
        """
        pass

    def at_post_puppet(self):
        super(Character, self).at_post_puppet()
        self.config.update_last_played()
        self.puppet_logs.create(player=self.player)

        # Update webclient data...
        self.who.add(self)
        self.web.full_update()

        if len(self.sessions.get()) == 1:
            self.at_true_login()

    def search_character(self, search_name=None, deleted=False):
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
        candidates = Character.objects.filter_family(character_settings__deleted=deleted)

        # First we'll run an Exact check.:
        search_results = self.search(search_name, exact=True, use_nicks=True, candidates=candidates, quiet=True)

        # Did that not work? Next we'll try the online match if it's set!
        if not search_results and not deleted:
            characters = self.who.ndb.characters
            search_results = self.search(search_name, exact=False, use_nicks=True, candidates=characters(),
                                         quiet=True)

        # We found NOBODY? Then error!
        if not search_results:
            raise ValueError("Character '%s' not found." % search_name)

        # We only want to return one result, even if multiple matches were found.
        if isinstance(search_results, list):
            return search_results[0]
        else:
            return search_results


    def sys_msg(self, message, sys_name='SYSTEM', error=False):
        # No use sending to a character that's not listening, is there?
        if not hasattr(self, 'player'):
            return

        if error:
            message = '|rERROR:|n %s' % message
        alert = '|%s-=<|n{%s%s|n|%s>=-|n ' % (self.player_config['msgborder_color'],
                                              self.player_config['msgtext_color'],
                                            sys_name.upper(), self.player_config['msgborder_color'])
        send_string = alert + message
        self.msg(unicode(ANSIString(send_string)))

    def mxp_name(self, commands=None):
        if not commands:
            commands = ['+finger']
        send_commands = '|'.join(['%s %s' % (command, self.key) for command in commands])
        return mxp(text=self.key, command=send_commands)

    @lazy_property
    def owner(self):
        return self.config.model.player

    @lazy_property
    def player_config(self):
        return self.owner.config

    def oob(self, *args, **kwargs):
        for sess in [sess for sess in self.sessions.get() if sess.ndb.gui]:
            sess.msg(*args, **kwargs)

    def rename(self, new_name):
        exist_ids = CharacterSetting.objects.filter(deleted=False).values_list('character', flat=True)
        exist = Character.objects.filter_family(id__in=exist_ids, db_key__iexact=new_name).exclude(id=self.id).count()
        if exist:
            raise ValueError("Character names must be unique!")
        self.key = new_name

    def at_rename(self, oldname, newname):
        from athanor.utils.create import CHARACTER_MANAGER
        CHARACTER_MANAGER.update(self)