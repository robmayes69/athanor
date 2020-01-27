from django.conf import settings
from evennia.utils.utils import class_from_module
from evennia import default_cmds
from evennia.commands.default import general

from athanor.commands import character

CMDSETS = [class_from_module(cmdset) for cmdset in settings.CMDSETS["CHARACTER"]]


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
        self.remove(general.CmdLook)
        self.add(character.CmdLook)

        for cmdset in CMDSETS:
            if hasattr(cmdset, "setup"):
                cmdset.setup(self)
            self.add(cmdset)
