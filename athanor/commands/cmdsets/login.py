from django.conf import settings
from evennia import default_cmds

USE_COMMANDS = []

USE_LISTS = [USE_COMMANDS]


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
        for cmdlist in USE_LISTS:
            for cmd in cmdlist:
                self.add(cmd)
