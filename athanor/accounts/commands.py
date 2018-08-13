from athanor.base.commands import AthCommand


class CmdLook(AthCommand):
    key = 'look'
    aliases = ('dir', 'ls', 'l', 'view','login')

    def _main(self):
        self.msg(self.account.at_look(target=self.account, session=self.session))


class CmdCharCreate(AthCommand):

    key = '@charcreate'
    locks = 'cmd:pperm(Player)'
    help_category = 'General'

    def _main(self):
        self.account.ath['character'].create(name=self.lhs)
