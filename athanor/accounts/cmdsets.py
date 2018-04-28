from athanor.base.cmdsets import AccountCmdSet as oldSet

from athanor.accounts.commands import AccountCmdIC, AccountCmdLook, AccountCmdCharCreate


class AccountCoreCmdSet(oldSet):
    command_classes = (AccountCmdIC, AccountCmdLook, AccountCmdCharCreate)