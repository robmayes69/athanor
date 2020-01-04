from django.conf import settings
from evennia import default_cmds
from athanor.forum.commands import ALL_COMMANDS as BBS_COMMANDS
from athanor.building.exit_errors import ExitErrorCmdSet
from athanor.themes.commands import CmdTheme
from athanor.mush_import.commands import CmdPennImport
from athanor.factions.commands import FACTION_COMMANDS
from athanor.accounts.commands import CmdAccount

USE_COMMANDS = [CmdTheme, CmdPennImport, CmdAccount]

USE_LISTS = [BBS_COMMANDS, FACTION_COMMANDS, USE_COMMANDS]


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
