from athanor.base.cmdsets import AthCmdSet
from athanor.staff.commands import CmdStaff


class StaffListCmdSet(AthCmdSet):
    command_classes = (CmdStaff, )
