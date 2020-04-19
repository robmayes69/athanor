from evennia import default_cmds
from evennia.commands.cmdset import CmdSet
from evennia.commands.default import account, admin, building, general
from athanor.commands import accounts as ath_account

from evennia.commands.default import unloggedin
from athanor.commands import login


class ServerSessionUnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Connection before being logged in.  This
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


class ServerSessionLoggedInCmdSet(CmdSet):
    """
    This Cmdset replaces UnloggedIn once a ServerSession has authenticated.
    It provides the Character Select screen / menu. It will be replaced again
    once a PlaySession is started.
    """
    key = "DefaultLoggedIn"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()

        self.add(ath_account.CmdAccRename)
        self.add(ath_account.CmdAccEmail)
        self.add(ath_account.CmdAccPassword)

        self.add(ath_account.CmdCharCreate)
        self.add(ath_account.CmdCharDelete)
        self.add(ath_account.CmdCharRename)

        self.add(ath_account.CmdCharPuppet)


class ServerSessionActiveCmdSet(CmdSet):
    """
    This CmdSet is active on ServerSession after a PlaySession has been linked.
    This makes the 'character select menu' go away.
    """
    key = "DefaultActive"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()

        self.add(ath_account.CmdCharUnpuppet)


class AccountCmdSet(default_cmds.AccountCmdSet):
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


class PlaySessionCmdSet(CmdSet):
    """
    This CmdSet is the base for all PlaySessions. Commands in this CmdSet are specific to the state of
    'being in play'.
    """

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()


class PlayerCharacterCmdSet(CmdSet):
    """
    This CmdSet contains
    """
    key = "DefaultPlayerCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class AvatarCmdSet(default_cmds.CharacterCmdSet):
    """
    The AvatarCmdSet is commands provided by the Object being puppeted as an Avatar.
    This will generally be
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
