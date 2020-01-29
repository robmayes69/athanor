from django.conf import settings
from athanor.commands.command import AthanorCommand


class AdministrationCommand(AthanorCommand):
    help_category = "Account Management"


class CmdAccount(AdministrationCommand):
    """
    General command for controlling game accounts.
    Note that <account> accepts either username or email address.

    Usage:
        @account <account>
            Display a breakdown of information all about an Account.

        @account/list
            Show all accounts in the system.

        @account/create <username>,<email>,<password>
            Create a new account.

        @account/disable <account>=<reason>
            Indefinitely disable an Account. The stated reason will be shown to all parties and recorded.
            If the account is currently online, it will be booted.
            Use @account/enable <account>=<reason> to re-enable the account.

        @account/ban <account>=<duration>,<reason>
            Temporarily disable an account until the timer's up. <duration> must be a time period such as
            7d (7 days), 2w (2 weeks), etc. Reason will be shown to the account and staff and recorded.
            Use @account/unban <account>=<reason> to lift it early.

        @account/rename <account>=<new name>
            Change an account's Username.

        @account/email <account>=<new email>
            Change an Account's email address.

        @account/password <account>=<new password>
            Re-set an Account's password.

        @account/grant <account>=<role>
            Grant a Role to an Account. See @role to know which are available.
            Use @account/revoke <account>=<role> to remove one.

        @account/addperm <account>=<permission>
            Grant an Evennia Permission to an Account. (Superuser only.)
            Use @account/delperm <account>=<permission> to remove it.

        @account/boot <account>=<reason>
            Forcibly disconnect an Account.

        @account/super <account>
            Promote an Account to Superuser status. (Superuser only.) Use again to demote. |rDANGEROUS.|n
    """
    key = '@account'
    locks = "cmd:pperm(Helper)"
    switch_options = ('list', 'create', 'disable', 'enable', 'rename', 'ban', 'unban', 'password', 'email', 'addperm',
                      'delperm', 'grant', 'revoke', 'super', 'boot')
    account_caller = True

    def switch_main(self):
        if not self.args:
            raise ValueError("Usage: @account <account>")
        self.controllers.get('account').examine_account(self.args)

    def switch_list(self):
        self.controllers.get('account').list_accounts(self.session)

    def switch_create(self):
        if not len(self.arglist) == 3:
            raise ValueError("Usage: @account/create <username>,<email>,<password>")
        username, email, password = self.arglist
        self.controllers.get('account').create_account(self.session, username, email, password)

    def switch_disable(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/disable <account>=<reason>")
        self.controllers.get('account').disable_account(self.session, self.lhs, self.rhs)

    def switch_enable(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/enable <account>=<reason>")
        self.controllers.get('account').enable_account(self.session, self.lhs, self.rhs)

    def switch_rename(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/rename <account>=<new name>")
        self.controllers.get('account').rename_account(self.session, self.lhs, self.rhs)

    def switch_ban(self):
        if not (self.lhs and self.rhs) or not len(self.rhslist) == 2:
            raise ValueError("Usage: @account/ban <account>=<duration>,<reason>")
        self.controllers.get('account').ban_account(self.session, self.lhs, self.rhslist[0], self.rhslist[1])

    def switch_unban(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/ban <account>=<reason>")
        self.controllers.get('account').unban_account(self.session, self.lhs, self.rhs)

    def switch_password(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/password <account>=<new password>")
        self.controllers.get('account').reset_password(self.session, self.lhs, self.rhs)

    def switch_email(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/email <account>=<new email>")
        self.controllers.get('account').change_email(self.session, self.lhs, self.rhs)

    def switch_addperm(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/addperm <account>=<new permission>")
        self.controllers.get('account').add_permission(self.session, self.lhs, self.rhs)

    def switch_delperm(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/delperm <account>=<delete permission>")
        self.controllers.get('account').delete_permission(self.session, self.lhs, self.rhs)

    def switch_grant(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/grant <account>=<new role>")
        self.controllers.get('account').grant_role(self.session, self.lhs, self.rhs)

    def switch_revoke(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/revoke <account>=<role to remove>")
        self.controllers.get('account').revoke_role(self.session, self.lhs, self.rhs)


class CmdCharacter(AdministrationCommand):
    """
    Help coming soon.
    """
    key = '@character'
    locks = "cmd:pperm(Helper)"
    switch_options = ('list', 'search', 'enable', 'disable', 'lock',
                      'typeclass', 'status', 'puppet', 'cost', 'create', 'account', 'shelved', 'examine')

    def switch_main(self):
        self.controllers.get('character').account_list(self.session, self.args)

    def switch_search(self):
        pass

    def switch_enable(self):
        pass

    def switch_disable(self):
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

    def switch_rename(self):
        pass

    def switch_transfer(self):
        pass

    def switch_old(self):
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
