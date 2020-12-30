from evennia.commands.default import help, comms, admin, system
from evennia.commands.default import building, account, general
from athanor.accounts import commands as athcmds
from athanor.utils.cmdset import BaseAthCmdSet


class AccountCmdSet(BaseAthCmdSet):
    key = "AccountCmdSet"
    priority = -10
    family = "account"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()

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

        self.add(athcmds.CmdAccess)
        self.add(athcmds.CmdAccount)

        #self.add(athcmds.CmdAddAcl)
        #self.add(athcmds.CmdGetAcl)
        #self.add(athcmds.CmdRemAcl)
