from evennia import default_cmds
from evennia.commands.cmdset import CmdSet
from evennia.commands.default import account, admin, building, general
from athanor.commands import accounts as ath_account

from evennia.commands.default import unloggedin
from athanor.commands import login


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
        self.remove(unloggedin.CmdUnconnectedConnect)
        self.add(login.CmdLoginCreateAccount)
        self.add(login.CmdLoginHelp)
        self.add(login.CmdLoginConnect)


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



class AthanorCharacterCmdSet(CmdSet):
    """

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


class AthanorAvatarCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """
    key = "DefaultAvatar"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
