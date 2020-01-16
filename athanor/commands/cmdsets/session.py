from django.conf import settings

from evennia import default_cmds

CMDSETS_LOADED = False

USE_LISTS = []


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
        global CMDSETS_LOADED, USE_LISTS
        if not CMDSETS_LOADED:
            from django.conf import settings
            from evennia.utils.utils import class_from_module
            for cmdset_path in settings.CMDSETS_SESSION:
                USE_LISTS.append(class_from_module(cmdset_path))
            CMDSETS_LOADED = True

        for cmdlist in USE_LISTS:
            for cmd in cmdlist:
                self.add(cmd)
