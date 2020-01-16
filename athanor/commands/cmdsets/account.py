from evennia import default_cmds

CMDSETS_LOADED = False

USE_LISTS = []


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
        global CMDSETS_LOADED, USE_LISTS
        if not CMDSETS_LOADED:
            from django.conf import settings
            from evennia.utils.utils import class_from_module
            for cmdset_path in settings.CMDSETS_ACCOUNT:
                USE_LISTS.append(class_from_module(cmdset_path))
            CMDSETS_LOADED = True

        for cmdlist in USE_LISTS:
            for cmd in cmdlist:
                self.add(cmd)
