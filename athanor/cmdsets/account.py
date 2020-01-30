from django.conf import settings
from evennia.utils.utils import class_from_module
from evennia import default_cmds
from evennia.commands.default import account, admin, building, general
from athanor.commands import accounts as ath_account


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
        self.remove(account.CmdCharCreate)
        self.remove(account.CmdCharDelete)
        self.remove(account.CmdIC)
        self.remove(account.CmdOOC)
        self.remove(admin.CmdNewPassword)
        self.remove(building.CmdExamine)
        self.remove(admin.CmdPerm)
        self.remove(general.CmdAccess)
        self.remove(admin.CmdBan)
        self.remove(admin.CmdBoot)
        self.remove(admin.CmdUnban)
        self.remove(admin.CmdWall)
        self.remove(admin.CmdEmit)
        self.remove(account.CmdPassword)

        self.add(ath_account.CmdAccess)

        self.add(ath_account.CmdAccount)
        self.add(ath_account.CmdCharacter)

        self.add(ath_account.CmdAccRename)
        self.add(ath_account.CmdAccEmail)
        self.add(ath_account.CmdAccPassword)

        self.add(ath_account.CmdCharCreate)
        self.add(ath_account.CmdCharDelete)
        self.add(ath_account.CmdCharRename)
        self.add(ath_account.CmdCharPuppet)
        self.add(ath_account.CmdCharUnpuppet)

        for cmdset in CMDSETS:
            if hasattr(cmdset, "setup"):
                cmdset.setup(self)
            self.add(cmdset)
