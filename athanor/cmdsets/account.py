from django.conf import settings
from evennia.utils.utils import class_from_module
from evennia import default_cmds

CMDSETS = [class_from_module(cmdset) for cmdset in settings.CMDSETS["ACCOUNT"]]


class AthanorAccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """
    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        for cmdset in CMDSETS:
            if hasattr(cmdset, "setup"):
                cmdset.setup(self)
            self.add(cmdset)
