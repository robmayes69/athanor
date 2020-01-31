from django.conf import settings
from athanor.commands.command import AthanorCommand


class AdministrationCommand(AthanorCommand):
    help_category = "Account Management"


class CmdAccount(AdministrationCommand):
    """
    General command for controlling game accounts.
    Note that <account> accepts either username or email address.

    Usage:
        @account [<account>]
            Display a breakdown of information all about an Account.
            Your own, if not targeted.

        @account/list
            Show all accounts in the system.

        @account/create <username>,<email>,<password>
            Create a new account.

        @account/disable <account>=<reason>
            Indefinitely disable an Account. The stated reason will be shown
            to staff and the account. If the account is currently online,
            it will be booted.
            Use @account/enable <account> to re-enable the account.

        @account/ban <account>=<duration>,<reason>
            Temporarily disable an account until the timer's up. <duration>
            must be a time period such as 7d (7 days), 2w (2 weeks), etc.
            Reason will be shown to the account and staff and recorded.
            Use @account/unban <account> to lift it early.

        @account/rename <account>=<new name>
            Change an account's Username.

        @account/email <account>=<new email>
            Change an Account's email address.

        @account/password <account>=<new password>
            Re-set an Account's password.

        @account/boot <account>=<reason>
            Forcibly disconnect an Account.
    """
    key = '@account'
    locks = "cmd:pperm(Helper)"
    switch_options = ('list', 'create', 'disable', 'enable', 'rename', 'ban', 'unban', 'password', 'email', 'addperm',
                      'delperm', 'grant', 'revoke', 'super', 'boot')
    account_caller = True

    def switch_main(self):
        if not self.args:
            self.args = self.account
        self.msg(self.controllers.get('account').examine_account(self.session, self.args))

    def switch_list(self):
        self.msg(self.controllers.get('account').list_accounts(self.session))

    def switch_create(self):
        if not len(self.argscomma) == 3:
            raise ValueError("Usage: @account/create <username>,<email>,<password>")
        username, email, password = self.argscomma
        self.controllers.get('account').create_account(self.session, username, email, password)

    def switch_disable(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/disable <account>=<reason>")
        self.controllers.get('account').disable_account(self.session, self.lhs, self.rhs)

    def switch_enable(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/enable <account>")
        self.controllers.get('account').enable_account(self.session, self.args)

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
            raise ValueError("Usage: @account/ban <account>")
        self.controllers.get('account').unban_account(self.session, self.args)

    def switch_password(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/password <account>=<new password>")
        self.controllers.get('account').reset_password(self.session, self.lhs, self.rhs)

    def switch_email(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/email <account>=<new email>")
        self.controllers.get('account').change_email(self.session, self.lhs, self.rhs)

    def switch_boot(self):
        self.controllers.get('account').disconnect_account(self.session, self.lhs, self.rhs)


class CmdAccess(AdministrationCommand):
    """
    Displays and manages information about Account access permissions.

    Usage:
        @access [<account>]
            Show the target's access details. Your own, if none is provided.

        @access/grant <account>=<permission>
            Grant an Evennia Permission to an Account.
            Use @access/revoke <account>=<permission> to remove it.

        @access/all
            Displays all grantable normal Permissions and their descriptions.

        @access/directory
            Display all managed Permissions and which Accounts hold them.
            Could be very spammy.

        @access/super <account>=SUPER DUPER
            Promote an Account to Superuser status. Use again to demote.
            Silly verification string required for accident prevention.
            |rDANGEROUS.|n
    """
    key = "@access"
    locks = "cmd:pperm(Helper)"
    switch_options = ("directory", "all", "grant", "revoke", "super")

    def switch_main(self):
        account = self.args if self.args else self.account
        self.msg(self.controllers.get('account').access_account(self.session, account))

    def switch_grant(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/grant <account>=<new permission>")
        self.controllers.get('account').grant_permission(self.session, self.lhs, self.rhs)

    def switch_revoke(self):
        if not self.lhs and self.rhs:
            raise ValueError("Usage: @account/revoke <account>=<delete permission>")
        self.controllers.get('account').revoke_permission(self.session, self.lhs, self.rhs)

    def switch_super(self):
        if not self.args:
            raise ValueError("Usage: @account/super <account>=SUPER DUPER")
        if self.rhs != "SUPER DUPER":
            raise ValueError("Usage: @account/super <account>=SUPER DUPER")
        self.controllers.get('account').toggle_super(self.session, self.lhs)

    def switch_all(self):
        self.msg(self.controllers.get('account').list_permissions(self.session))

    def switch_directory(self):
        self.msg(self.controllers.get('account').permissions_directory(self.session))


class CmdCharacter(AdministrationCommand):
    """
    Help coming soon.
    """
    key = '@character'
    locks = "cmd:pperm(Helper)"
    switch_options = ('list', 'archive', 'restore', 'rename', 'puppet', 'create', 'transfer', 'old')

    def switch_main(self):
        self.msg(self.controllers.get('character').examine_character(self.session, self.args))

    def switch_create(self):
        self.controllers.get('character').create_character(self.session, self.lhs, self.rhs)

    def switch_restore(self):
        self.controllers.get('character').restore_character(self.session, self.lhs, self.rhs)

    def switch_archive(self):
        self.controllers.get('character').archive_character(self.session, self.args)

    def switch_puppet(self):
        self.controllers.get('character').puppet_character(self.session, self.args)

    def switch_rename(self):
        self.controllers.get('character').rename_character(self.session, self.lhs, self.rhs)

    def switch_transfer(self):
        self.controllers.get('character').transfer_character(self.session, self.lhs, self.rhs)

    def switch_old(self):
        self.controllers.get('character').list_archived(self.session)

    def switch_list(self):
        self.msg(self.controllers.get('character').list_characters(self.session))


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
    """
    Create a character bound to your account!

    Usage:
        @charcreate <character name>
    """
    key = '@charcreate'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_CHARACTER_CREATION else 'all()'
    account_caller = True

    def switch_main(self):
        self.controllers.get('character').create_character(self.session, self.caller, self.args, ignore_priv=True)


class CmdCharRename(AdministrationCommand):
    """
    Rename a character you own.

    Usage:
        @charrename <character>=<new name>
    """
    key = "@charrename"
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_CHARACTER_RENAME else 'all()'
    account_caller = True

    def switch_main(self):
        character = self.select_character(self.lhs)
        self.controllers.get('character').rename_character(self.session, character, self.rhs)


class CmdCharDelete(AdministrationCommand):
    """
    Delete one of your characters.

    Usage:
        @chardelete <character>=<verify name>
    """
    key = '@chardelete'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_CHARACTER_DELETION else 'all()'
    account_caller = True

    def switch_main(self):
        character = self.select_character(self.lhs)
        self.controllers.get('character').delete_character(self.session, character, self.rhs, ignore_priv=True)


class CmdCharPuppet(AdministrationCommand):
    """
    Enter game as one of your characters.

    Usage:
        @ic <character>
    """
    key = "@ic"
    locks = "cmd:all()"
    account_caller = True

    def switch_main(self):
        character = self.select_character(self.args)
        self.caller.puppet_object(self.session, character)


class CmdCharUnpuppet(AdministrationCommand):
    """
    Have your puppeted character leave the game world. Return to the
    account menu.

    Usage:
        @ooc
    """
    key = "@ooc"
    locks = "cmd:all()"
    account_caller = True

    def switch_main(self):
        if not self.session.get_puppet():
            raise ValueError("Can only use this while @ic!")
        self.caller.unpuppet_object(self.session)
        self.msg(self.caller.render_character_menu(self))
