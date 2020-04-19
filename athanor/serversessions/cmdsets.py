from evennia.commands.cmdset import CmdSet
from athanor.serversessions import cmds_login, cmds_select, cmds_active
from evennia.commands.default import unloggedin


class LoginCmdSet(CmdSet):
    key = "LoginCmdSet"

    def at_cmdset_creation(self):
        self.add(cmds_login.CmdLoginCreateAccount)
        self.add(cmds_login.CmdLoginConnect)
        self.add(cmds_login.CmdLoginHelp)
        self.add(unloggedin.CmdUnconnectedQuit)
        self.add(unloggedin.CmdUnconnectedEncoding)
        self.add(unloggedin.CmdUnconnectedInfo)
        self.add(unloggedin.CmdUnconnectedLook)
        self.add(unloggedin.CmdUnconnectedScreenreader)


class CharacterSelectScreenCmdSet(CmdSet):
    key = "CharacterSelectScreenCmdSet"

    def at_cmdset_creation(self):
        self.add(cmds_select.CmdCharacterSelectLook)
