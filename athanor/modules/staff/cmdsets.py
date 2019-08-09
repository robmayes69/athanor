from athanor.base.cmdsets import AthCmdSet
from athanor.modules.staff import CmdStaff


class StaffListCmdSet(AthCmdSet):
    command_classes = (CmdStaff, )
