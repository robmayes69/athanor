from django.conf import settings
from evennia import default_cmds

CMDSETS_LOADED = False

USE_LISTS = []


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
        global CMDSETS_LOADED, USE_LISTS
        if not CMDSETS_LOADED:
            from evennia.utils.utils import class_from_module
            for cmdset_path in settings.CMDSETS_LOGIN:
                USE_LISTS.append(class_from_module(cmdset_path))
            CMDSETS_LOADED = True

        for cmdlist in USE_LISTS:
            for cmd in cmdlist:
                self.add(cmd)
