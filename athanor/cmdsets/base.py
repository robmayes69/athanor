from evennia.commands.cmdset import CmdSet


class AccountCmdSet(CmdSet):
    priority = -9


class CharacterCmdSet(CmdSet):
    priority = 1


class UnloggedCmdSet(CmdSet):
    priority = -19