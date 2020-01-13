from django.conf import settings
from evennia import default_cmds

USE_COMMANDS = []

USE_LISTS = [USE_COMMANDS]


class AthanorSessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """
    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some note.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        for cmdlist in USE_LISTS:
            for cmd in cmdlist:
                self.add(cmd)
