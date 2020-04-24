from django.conf import settings
from athanor.utils.command import AthanorCommand
from evennia.commands.cmdhandler import CMD_LOGINSTART
from athanor.accounts.commands import AdministrationCommand


class CmdCharacterSelectLook(AthanorCommand):
    key = CMD_LOGINSTART
    aliases = ["look", "l"]
    locks = "cmd:all()"

    def switch_main(self):
        self.session.msg(self.account.appearance.render(self.session))


class CmdAccRename(AdministrationCommand):
    """
    Change your Username!

    Usage:
        @username <new name>
    """
    key = '@username'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_ACCOUNT_RENAME else 'all()'

    def switch_main(self):
        self.controller.rename_account(self.session, self.caller, self.args, ignore_priv=True)


class CmdAccEmail(AdministrationCommand):
    """
    Change your Account Email address!

    Usage:
        @email <new email>
    """
    key = '@email'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_ACCOUNT_EMAIL else 'all()'

    def switch_main(self):
        self.controller.email_account(self.session, self.caller, self.args, ignore_priv=True)


class CmdAccPassword(AdministrationCommand):
    """
    Change your login password!

    Usage:
        @password <old>=<new>
    """
    key = '@password'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_ACCOUNT_PASSWORD else 'all()'

    def switch_main(self):
        if not self.rhs and self.lhs:
            raise ValueError(f"Usage: @password <old>=<new>")
        self.controller.password_account(self.session, self.caller, self.rhs, ignore_priv=True,
                                                       old_password=self.lhs)


class CmdCharCreate(AdministrationCommand):
    """
    Create a character bound to your account!

    Usage:
        @charcreate <character name>
    """
    key = '@charcreate'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_CHARACTER_CREATION else 'all()'
    controller_key = 'playercharacter'

    def switch_main(self):
        self.controller.create_character(self.session, self.caller, self.args, ignore_priv=True)


class CmdCharRename(AdministrationCommand):
    """
    Rename a character you own.

    Usage:
        @charrename <character>=<new name>
    """
    key = "@charrename"
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_CHARACTER_RENAME else 'all()'
    controller_key = 'playercharacter'

    def switch_main(self):
        character = self.select_character(self.lhs)
        self.controller.rename_character(self.session, character, self.rhs)


class CmdCharDelete(AdministrationCommand):
    """
    Delete one of your characters.

    Usage:
        @chardelete <character>=<verify name>
    """
    key = '@chardelete'
    locks = 'cmd:%s' % 'pperm(Admin)' if settings.RESTRICTED_CHARACTER_DELETION else 'all()'
    controller_key = 'playercharacter'

    def switch_main(self):
        character = self.select_character(self.lhs)
        self.controller.delete_character(self.session, character, self.rhs, ignore_priv=True)


class CmdCharSelect(AdministrationCommand):
    help_category = "Play Session Commands"
    key = "@select"
    controller_key = 'playercharacter'

    def switch_main(self):
        character = self.select_character(self.lhs)
        psesscon = self.controllers.get('playsession')
        psess = psesscon.get(character)
        self.session.link_play_session(psess)


class CmdEndPlaySession(AdministrationCommand):
    help_category = "Play Session Commands"
    key = "@end"
    controller_key = 'playercharacter'

    def switch_main(self):
        pass


class CmdQuit(AthanorCommand):
    help_category = "General"
    key = "QUIT"

    def switch_main(self):
        pass
