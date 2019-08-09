from athanor.base.cmdsets import AccountCmdSet

from athanor.modules.awho.accounts import CmdWho

class AWhoCmdSet(AccountCmdSet):
    key = 'awho'
    command_classes = (CmdWho,)