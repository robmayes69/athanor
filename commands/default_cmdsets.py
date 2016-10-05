"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from athanor.commands.evennia_cmdsets import CharacterCmdSet as OldCharacter, SessionCmdSet as OldSession, \
    UnloggedinCmdSet as OldUnlogged, PlayerCmdSet as OldPlayer
from athanor.commands.community import CmdWho
from athanor.info.info_files import CmdInfo
from athanor.bbs.bbs import CmdBBAdmin, CmdBBList, CmdBBRead, CmdBBWrite, CmdGBAdmin, CmdGBList, CmdGBRead, CmdGBWrite
from athanor.commands.account_management import CmdPlayerConfig, CmdTz, CmdWatch, CmdAccount
from athanor.commands.admin import CmdPlayers, CmdGameConfig, CmdAdmin
from athanor.groups.groups import GROUP_COMMANDS
from athanor.grid.grid_management import DISTRICT_COMMANDS
from athanor.commands.mush_import import CmdImport
from athanor.commands.login import CmdMushConnect, CmdCharCreate
from athanor.core.channels import CmdChannels
from athanor.radio.radio import CmdRadio
from athanor.fclist.fclist import CmdFCList
from athanor.commands.help import CmdHelp, CmdAdminHelp
from athanor.scenes.scene import CmdEvents

class CharacterCmdSet(OldCharacter):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `PlayerCmdSet` when a Player puppets a Character.
    """
    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super(CharacterCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdInfo())
        self.add(CmdBBAdmin())
        self.add(CmdBBList())
        self.add(CmdBBRead())
        self.add(CmdBBWrite())
        self.add(CmdGBAdmin())
        self.add(CmdGBList())
        self.add(CmdGBRead())
        self.add(CmdGBWrite())
        for group_cmd in GROUP_COMMANDS:
            self.add(group_cmd())
        for district_cmd in DISTRICT_COMMANDS:
            self.add(district_cmd())
        self.add(CmdImport())
        self.add(CmdPlayers())
        self.add(CmdGameConfig())
        self.add(CmdChannels())
        self.add(CmdRadio())
        self.add(CmdFCList())
        self.add(CmdEvents())
        self.add(CmdAccount())
        self.add(CmdPlayerConfig())


class PlayerCmdSet(OldPlayer):
    """
    This is the cmdset available to the Player at all times. It is
    combined with the `CharacterCmdSet` when the Player puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """
    key = "DefaultPlayer"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super(PlayerCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        #self.add(CmdOOCLook())
        self.add(CmdWho())
        self.add(CmdCharCreate())
        self.add(CmdHelp())
        self.add(CmdAdminHelp())
        self.add(CmdAdmin())


class UnloggedinCmdSet(OldUnlogged):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """
    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super(UnloggedinCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdMushConnect())


class SessionCmdSet(OldSession):
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
        It prints some info.
        """
        super(SessionCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
