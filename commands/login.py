from __future__ import unicode_literals
import re, time
from django.conf import settings
from evennia.utils import create
from typeclasses.characters import Character
from evennia.utils.create import create_player
from commands.command import MuxCommand, AthCommand
from evennia.commands.default.unloggedin import _LATEST_FAILED_LOGINS, _throttle

class CmdMushConnect(MuxCommand):
    """
    Connect to the game using an old Mush Login.
    This only works if the account hasn't been fully converted yet.
    Aliases do not function in this mode.

    Usage:
        penn charactername password
        penn "character name" "pass word"

    Enclose character names that have spaces in " ".
    """

    key = 'mush'
    aliases = ['penn']
    locks = "cmd:all()"  # not really needed
    arg_regex = r"\s.*?|$"

    def func(self):
        session = self.caller

        # check for too many login errors too quick.
        if _throttle(session, maxlim=5, timeout=5*60, storage=_LATEST_FAILED_LOGINS):
            # timeout is 5 minutes.
            session.msg("{RYou made too many connection attempts. Try again in a few minutes.{n")
            return

        args = self.args
        # extract quoted parts
        parts = [part.strip() for part in re.split(r"\"|\'", args) if part.strip()]
        if len(parts) == 1:
            # this was (hopefully) due to no quotes being found, or a guest login
            parts = parts[0].split(None, 1)
            # Guest login
            if len(parts) == 1 and parts[0].lower() == "guest" and settings.GUEST_ENABLED:
                session.msg("Guest logins through old import are not allowed.")
                return

        if len(parts) != 2:
            session.msg("\n\r Usage (without <>): connect <name> <password>")
            return
        playername, password = parts

        # Match old character name and check password
        char = Character.objects.filter_family(db_key__iexact=playername).first()
        if not char:
            session.msg("Character not found.")
            return
        old_char = char.mush
        if not old_char:
            session.msg("Character has no old data!")
            return
        player = char.db._owner
        if not player:
            session.msg("Character is not bound to a valid account.")
            return
        if not old_char.check_password(password):
            session.msg("Invalid password.")
            _throttle(session, storage=_LATEST_FAILED_LOGINS)
            return
        if not char.db._import_ready:
            session.msg("Character has already been imported or was not originally from PennMUSH. Contact an admin\nif this is in error.")
            return
        if player.db._lost_and_found:
            session.msg("Credentials accepted. Character is in the Lost and Found.\nCreating a new account for them.")
            create_name = unicode(float(time.time())).replace('.', '-')
            new_player = create_player(create_name, email=None, password=password)
            new_player.db._was_lost = True
            new_player.db._reset_email = True
            new_player.db._reset_username = True
            new_player.bind_character(char)
            session.msg("Your temporary account name is: %s" % create_name)
            session.msg("Account created, using your PennMUSH password.")
        else:
            session.msg("Credentials accepted. You can now login to this account with the given password.\nPlease set your username and email with the listed commands.")
            new_player = player
            new_player.set_password(password)
        session.msg("Import process complete!")
        for character in new_player.get_all_characters():
            del character.db._import_ready
        session.sessionhandler.login(session, new_player)


class CmdCharCreate(AthCommand):
    """
    create a new character

    Usage:
      @charcreate <charname> [= desc]

    Create a new character, optionally giving it a description. You
    may use upper-case letters in the name - you will nevertheless
    always be able to access your character using lower-case letters
    if you want.
    """
    key = "@charcreate"
    locks = "cmd:pperm(Players)"
    help_category = "General"

    def func(self):
        "create the new character"
        player = self.player
        if not self.args:
            self.msg("Usage: @charcreate <charname> [= description]")
            return
        key = self.lhs
        desc = self.rhs

        charmax = settings.MAX_NR_CHARACTERS if settings.MULTISESSION_MODE > 1 else 1

        if not player.is_superuser and \
            (player.db._playable_characters and
                len(player.db._playable_characters) >= charmax):
            self.msg("You may only create a maximum of %i characters." % charmax)
            return
        # create the character
        from evennia.objects.models import ObjectDB

        start_location = ObjectDB.objects.get_id(settings.START_LOCATION)
        default_home = ObjectDB.objects.get_id(settings.DEFAULT_HOME)
        typeclass = settings.BASE_CHARACTER_TYPECLASS
        permissions = settings.PERMISSION_PLAYER_DEFAULT

        new_character = create.create_object(typeclass, key=key,
                                             location=start_location,
                                             home=default_home,
                                             permissions=permissions)
        # only allow creator (and immortals) to puppet this char
        new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" %
                                (new_character.id, player.id))
        player.bind_character(new_character)
        if desc:
            new_character.db.desc = desc
        elif not new_character.db.desc:
            new_character.db.desc = "This is a Player."
        self.msg("Created new character %s. Use {w@ic %s{n to enter the game as this character." % (new_character.key, new_character.key))