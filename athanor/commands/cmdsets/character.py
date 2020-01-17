from django.conf import settings

from evennia import default_cmds
from athanor.commands.exit_errors import ExitErrorCmdSet

CMDSETS_LOADED = False

USE_LISTS = []


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
        global CMDSETS_LOADED, USE_LISTS
        if not CMDSETS_LOADED:
            from evennia.utils.utils import class_from_module
            for cmdset_path in settings.CMDSETS["CHARACTER"]:
                USE_LISTS.append(class_from_module(cmdset_path))
            if settings.DIRECTIONAL_EXIT_ERRORS:
                USE_LISTS.append(ExitErrorCmdSet)
            CMDSETS_LOADED = True

        for cmdlist in USE_LISTS:
            for cmd in cmdlist:
                self.add(cmd)
