import re
from athanor.base.cmdsets import UnloggedCmdSet as oldSet
from athanor.base.commands import AthCommand
from athanor import AthException


class CmdLogin(AthCommand):
    key = 'login'
    locks = 'cmd:all()'

    def _main(self):
        if not self.lhs:
            raise AthException("No username/email entered!")
        account = self.systems['account'].search(self.caller, self.lhs)
        self.systems['account'].login(self.caller, account, self.rhs)


class CmdConnect(AthCommand):
    key = 'connect'
    locks = 'cmd:all()'

    def _main(self):
        parts = [part.strip() for part in re.split(r"\"", self.args) if part.strip()]
        if len(parts) == 1:
            # this was (hopefully) due to no double quotes being found, or a guest login
            parts = parts[0].split(None, 1)

        if len(parts) != 2:
            session.msg("\n\r Usage (without <>): connect <name> <password>")
            return

        name, password = parts
        account = self.systems['account'].search(self.caller, name)
        self.systems['account'].login(self.caller, account, password)


class CmdCreate(AthCommand):
    key = 'create'
    locks = 'cmd:all()'

    def _main(self):
        account = self.systems['account'].create(self.caller, self.lhs, self.rhs)
        self.systems['account'].login(self.caller, account, self.rhs)


class UnloggedCmdSet(oldSet):
    command_classes = (CmdLogin, CmdConnect, CmdCreate)
