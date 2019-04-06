from athanor.base.cmdsets import AthCmdSet
from athanor_staff.commands import CmdStaff


class StaffListCmdSet(AthCmdSet):
    command_classes = (CmdStaff, )
