from django.conf import settings

from evennia import default_cmds

from athanor.commands.forum import ALL_COMMANDS as FORUM_COMMANDS
from athanor.commands.exit_errors import ExitErrorCmdSet
from athanor.commands.themes import CmdTheme
from athanor.mush_import.commands import CmdPennImport
from athanor.commands.factions import FACTION_COMMANDS
from athanor.commands.accounts import CmdAccount

USE_COMMANDS = [CmdTheme, CmdPennImport, CmdAccount]

USE_LISTS = [FORUM_COMMANDS, FACTION_COMMANDS, USE_COMMANDS]


class AthanorCharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """
    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        if settings.DIRECTIONAL_EXIT_ERRORS:
            self.add(ExitErrorCmdSet)
        for cmdlist in USE_LISTS:
            for cmd in cmdlist:
                self.add(cmd)
