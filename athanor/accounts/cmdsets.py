from athanor.base.cmdsets import AccountCmdSet as oldSet

from athanor.accounts.commands import CmdIC, CmdLook, CmdCharCreate, CmdQuit


class OOCCmdSet(oldSet):
    command_classes = (CmdIC, CmdLook, CmdCharCreate)