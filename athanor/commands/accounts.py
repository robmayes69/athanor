from django.conf import settings
from athanor.commands.command import AthanorCommand
from athanor.utils import styling

class AdministrationCommand(AthanorCommand):
    help_category = "Administration"


class CmdAccount(AdministrationCommand):
    """
    Coming soon!
    """
    key = '@account'
    locks = "cmd:pperm(Helper)"
    switch_options = ('list', 'create', 'disable', 'enable', 'rename', 'ban', 'password', 'email', 'addperm',
                      'delperm', 'examine')
    account_caller = True

    def switch_main(self):
        pass

    def switch_list(self):
        if not self.caller.locks.check_lockstring(self.caller, "dummy:apriv(account_examine)"):
            raise ValueError("Permission denied.")
        if not (visible_accounts := self.controllers.get('account').visible_accounts()):
            raise ValueError("No accounts to list!")
        message = list()
        for account in visible_accounts:
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


class CmdCharacter(AdministrationCommand):
    """
    Help coming soon.
    """
    key = '@character'
    locks = "cmd:pperm(Helper)"
    switch_options = ('list', 'search', 'enable', 'disable', 'shelf', 'unshelf', 'ban', 'unban', 'lock',
                      'typeclass', 'status', 'puppet', 'cost', 'create', 'account', 'shelved', 'examine')

    def switch_main(self):
        pass

    def switch_search(self):
        pass

    def switch_enable(self):
        pass

    def switch_disable(self):
        pass

    def switch_shelf(self):
        pass

    def switch_unshelf(self):
        pass

    def switch_ban(self):
        pass

    def switch_unban(self):
        pass

    def switch_lock(self):
        pass

    def switch_status(self):
        pass

    def switch_typeclass(self):
        pass

    def switch_puppet(self):
        pass

    def switch_cost(self):
        pass

    def switch_create(self):
        pass

    def switch_account(self):
        pass

    def switch_shelved(self):
        pass


class CmdAccRename(AdministrationCommand):
    """
    Change your Username!

    Usage:
        @username <new name>
    """
    key = '@username'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_ACCOUNT_RENAME else 'all()'
    account_caller = True

    def switch_main(self):
        self.controllers.get('account').rename_account(self.session, self.caller, self.args, ignore_priv=True)


class CmdAccEmail(AdministrationCommand):
    """
    Change your Account Email address!

    Usage:
        @email <new email>
    """
    key = '@email'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_ACCOUNT_EMAIL else 'all()'
    account_caller = True

    def switch_main(self):
        self.controllers.get('account').change_email(self.session, self.caller, self.args, ignore_priv=True)


class CmdAccPassword(AdministrationCommand):
    """
    Change your login password!

    Usage:
        @password <old>=<new>
    """
    key = '@password'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_ACCOUNT_PASSWORD else 'all()'
    account_caller = True

    def switch_main(self):
        if not self.rhs and self.lhs:
            raise ValueError(f"Usage: @password <old>=<new>")
        self.controllers.get('account').reset_password(self.session, self.caller, self.rhs, ignore_priv=True,
                                                       old_password=self.lhs)


class CmdCharCreate(AdministrationCommand):
    key = '@charcreate'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_CHARACTER_CREATION else 'all()'
    account_caller = True

    def switch_main(self):
        self.controllers.get('character').create_character(self.session, self.caller, self.args, ignore_priv=True)


class CmdCharRename(AdministrationCommand):
    key = "@charrename"
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_CHARACTER_RENAME else 'all()'
    account_caller = True

    def switch_main(self):
        character = self.select_character(self.lhs)
        self.controllers.get('character').rename_character(self.session, character, self.rhs)


class CmdCharDelete(AdministrationCommand):
    key = '@chardelete'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_CHARACTER_DELETION else 'all()'
    account_caller = True

    def switch_main(self):
        character = self.select_character(self.lhs)
        self.controllers.get('character').delete_character(self.session, character, self.rhs, ignore_priv=True)


class CmdCharPuppet(AdministrationCommand):
    key = "@ic"
    locks = "cmd:all()"
    account_caller = True

    def switch_main(self):
        character = self.select_character(self.args)
        self.caller.puppet_object(self.session, character)


class CmdCharUnpuppet(AdministrationCommand):
    key = "@ooc"
    locks = "cmd:all()"
    account_caller = True

    def switch_main(self):
        if not self.session.get_puppet():
            raise ValueError("Can only use this while @ic!")
        self.caller.unpuppet_object(self.session)
        self.msg(self.caller.render_character_menu(self))
