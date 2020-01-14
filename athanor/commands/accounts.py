from athanor.commands.command import AthanorCommand


class CmdAccount(AthanorCommand):

    key = '@account'
    help_category = "Administration"
    switch_options = ('list', 'create', 'disable', 'enable', 'rename', 'ban', 'password', 'email', 'addperm', 'delperm')

    def switch_main(self):
        pass

    def switch_list(self):
        pass

    def switch_create(self):
        if not len(self.arglist) == 3:
            raise ValueError("Usage: @account/create <username>,<email>,<password>")
        username, email, password = self.arglist
        self.controllers.account.create_account(self.session, username, email, password)

    def switch_disable(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/disable <account>=<reason>")
        self.controllers.account.disable_account(self.session, self.lhs, self.rhs)

    def switch_enable(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/enable <account>=<reason>")
        self.controllers.account.enable_account(self.session, self.lhs, self.rhs)

    def switch_rename(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/rename <account>=<new name>")
        self.controllers.account.rename_account(self.session, self.lhs, self.rhs)

    def switch_ban(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/ban <account>=<duration>")
        self.controllers.account.ban_account(self.session, self.lhs, self.rhs)

    def switch_password(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/password <account>=<new password>")
        self.controllers.account.reset_password(self.session, self.lhs, self.rhs)

    def switch_email(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/email <account>=<new email>")
        self.controllers.account.change_email(self.session, self.lhs, self.rhs)

    def switch_addperm(self):
        pass

    def switch_delperm(self):
        pass
