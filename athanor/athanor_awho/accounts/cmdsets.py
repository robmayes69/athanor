from athanor.base.cmdsets import AccountCmdSet

from athanor.athanor_awho.accounts.commands import CmdWho

class AWhoCmdSet(AccountCmdSet):
    key = 'awho'
    command_classes = (CmdWho,)