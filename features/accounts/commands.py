from commands.command import Command


class CmdAccount(Command):

    key = '@account'
    help_category = "Administration"
    locks = "cmd:perm(Admin)"
    switch_options = ('list', 'create', 'edit', 'characters')

    def switch_main(self):
        self.msg("Unimplemented!")

    def switch_list(self):
        self.global_scripts.accounts.menu_search(self.session, self.caller)

    def switch_create(self):
        self.global_scripts.accounts.menu_create(self.session, self.caller)

    def switch_edit(self):
        self.global_scripts.accounts.menu_edit(self.session, self.caller, self.args)

    def switch_characters(self):
        self.global_scripts.accounts.menu_characters(self.session, self.caller, self.args)