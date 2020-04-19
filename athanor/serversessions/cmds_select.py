from athanor.utils.command import AthanorCommand
from evennia.commands.cmdhandler import CMD_LOGINSTART


class CmdCharacterSelectLook(AthanorCommand):
    key = CMD_LOGINSTART
    aliases = ["look", "l"]
    locks = "cmd:all()"

    def switch_main(self):
        self.session.msg(self.account.appearance.render(self.session))
