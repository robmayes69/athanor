from django.conf import settings
from evennia.utils.utils import class_from_module
from evennia import default_cmds
from evennia.commands.default import unloggedin

from athanor.commands import login

CMDSETS = [class_from_module(cmdset) for cmdset in settings.CMDSETS["ACCOUNT"]]


class AthanorUnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """
    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.remove(unloggedin.CmdUnconnectedCreate)
        self.remove(unloggedin.CmdUnconnectedHelp)
        self.add(login.CmdLoginCreateAccount)
        self.add(login.CmdLoginHelp)

        for cmdset in CMDSETS:
            if hasattr(cmdset, "setup"):
                cmdset.setup(self)
            self.add(cmdset)