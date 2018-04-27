from athanor.cmdsets.base import AccountCmdSet as oldSet

from athanor.commands.accounts import AccountCmdIC, AccountCmdLook, AccountCmdCharCreate


class AccountCoreCmdSet(oldSet):
    command_classes = (AccountCmdIC, AccountCmdLook, AccountCmdCharCreate)