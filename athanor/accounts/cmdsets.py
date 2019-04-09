from athanor.base.cmdsets import AccountCmdSet as oldSet

from athanor.accounts.commands import CmdLook, CmdCharCreate


class OOCCmdSet(oldSet):
    command_classes = (CmdLook, CmdCharCreate)


class StaffListCmdSet(AthCmdSet):
    command_classes = (CmdStaff, )