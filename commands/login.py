import re, traceback
from django.conf import settings
from evennia.players.models import PlayerDB
from typeclasses.characters import Character
from evennia.server.models import ServerConfig
from commands.command import MuxCommand
from commands.library import AthanorError
from evennia.commands.default.unloggedin import CmdUnconnectedConnect, _LATEST_FAILED_LOGINS, _throttle

class CmdMushConnect(MuxCommand):
    """
    Connect to the game using an old Mush Login.
    This only works if the account hasn't been fully converted yet.
    Aliases do not function in this mode.

    Usage:
        connect charactername password
        connect "character name" "pass word"

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
        char = Character.objects.filter(db_key__iexact=playername).first()
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
        session.sessionhandler.login(session, player)
