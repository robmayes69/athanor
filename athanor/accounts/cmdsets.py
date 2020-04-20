from evennia.commands.cmdset import CmdSet

from evennia.commands.default import help, comms, admin, system
from evennia.commands.default import building, account, general


class AccountCmdSet(CmdSet):
    key = "AccountCmdSet"
    priority = -10

    def at_cmdset_creation(self):
        self.add(account.CmdWho)
        self.add(account.CmdOption)
        self.add(account.CmdColorTest)
        self.add(account.CmdQuell)
        self.add(account.CmdStyle)

        # nicks
        self.add(general.CmdNick)

        # testing
        self.add(building.CmdExamine)

        # Help command
        self.add(help.CmdHelp)

        # system commands
        self.add(system.CmdReload)
        self.add(system.CmdReset)
        self.add(system.CmdShutdown)
        self.add(system.CmdPy)
