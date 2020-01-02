from athanor.core.command import AthanorCommand
from athanor.core.menu import AthanorMenu


class CmdAccount(AthanorCommand):

    key = '@account'
    help_category = "Administration"
    switch_options = ('list', 'create', 'disable', 'enable', 'rename', 'ban', 'password', 'email', 'addperm', 'delperm')

    def switch_main(self):
        AthanorMenu(self.caller, 'features.accounts.menu_create', startnode='node_main', session=self.session, menu_name='Account Editor')

    def switch_list(self):
        pass

    def switch_create(self):
        pass

    def switch_disable(self):
        pass

    def switch_enable(self):
        pass

    def switch_rename(self):
        pass

    def switch_ban(self):
        pass

    def switch_password(self):
        pass

    def switch_email(self):
        pass

    def switch_addperm(self):
        pass

    def switch_delperm(self):
        pass