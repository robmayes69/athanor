from athanor.cmdsets.base import AccountCmdSet as oldSet

from athanor.commands.accounts import AccountCmdIC, AccountCmdLook, AccountCmdCharCreate

class AthCoreAccountCmdSet(oldSet):

    def at_cmdset_creation(self):
        self.add(AccountCmdIC)
        self.add(AccountCmdLook)
        self.add(AccountCmdCharCreate)