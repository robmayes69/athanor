from athanor.base.cmdsets import AccountCmdSet, CharacterCmdSet, UnloggedCmdSet, SessionCmdSet

from evennia.commands.default import help, comms, admin, system
from evennia.commands.default import building, account, general


class AccountAdminCmdSet(AccountCmdSet):
    command_classes = (account.CmdQuell, system.CmdReload, system.CmdReset, system.CmdShutdown, system.CmdPy)


class AccountBaseCmdSet(AccountCmdSet):
    command_classes = (help.CmdHelp,)


class CharacterAdminCmdSet(CharacterCmdSet):
    command_classes = (system.CmdPy, system.CmdService, system.CmdServerLoad, system.CmdTickers, admin.CmdWall)


class CharacterBaseCmdSet(CharacterCmdSet):
    command_classes = (help.CmdHelp, general.CmdLook, general.CmdSay, general.CmdAccess, general.CmdWhisper, system.CmdTime, system.CmdAbout)