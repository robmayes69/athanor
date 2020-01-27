import datetime
from django.conf import settings

from evennia.utils.utils import class_from_module, lazy_property
from evennia.accounts.accounts import DefaultAccount

from athanor.utils.events import EventEmitter
from athanor.gamedb.handlers import RoleHandler, PrivilegeHandler
from athanor.gamedb.characters import AthanorPlayerCharacter

MIXINS = [class_from_module(mixin) for mixin in settings.GAMEDB_MIXINS["ACCOUNT"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorAccount(*MIXINS, DefaultAccount, EventEmitter):
    """
    AthanorAccount adds the EventEmitter to DefaultAccount and supports Mixins.
    Please read Evennia's documentation for its normal API.

    Triggers Global Events:
        account_connect (session): Fired whenever a Session authenticates to this account.
        account_disconnect (session): Triggered whenever a Session disconnects from this account.
        account_online (session): Fired whenever an account comes online from being completely offline.
        account_offline (session): Triggered when an account's final session closes.
    """

    def system_msg(self, text=None, system_name=None, enactor=None):
        sysmsg_border = self.options.sys_msg_border
        sysmsg_text = self.options.sys_msg_text
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def localize_timestring(self, time_data=None, time_format='%b %d %I:%M%p %Z', tz=None):
        if not time_data:
            time_data = datetime.datetime.utcnow()
        if not tz:
            tz = self.options.timezone
        return time_data.astimezone(tz).strftime(time_format)

    def __str__(self):
        return self.key

    @classmethod
    def create_account(cls, *args, **kwargs):
        account, errors = cls.create(*args, **kwargs)
        if account:
            return account
        else:
            raise ValueError(errors)

    def at_post_disconnect(self, **kwargs):
        super().at_post_disconnect(**kwargs)
        self.emit_global("account_disconnect")
        if not self.sessions.all():
            self.emit_global("account_offline")

    def at_post_login(self, session=None, **kwargs):
        super().at_post_login(session, **kwargs)
        self.emit_global("account_connect", session=session)
        if len(self.sessions.all()) == 1:
            self.emit_global("account_online", session=session)

    @lazy_property
    def privileges(self):
        return PrivilegeHandler(self, "ACCOUNT")

    @lazy_property
    def roles(self):
        return RoleHandler(self)

    def set_email(self, new_email):
        new_email = self.__class__.objects.normalize_email(new_email)
        self.email = new_email
        return new_email

    def rename(self, new_name):
        new_name = self.normalize_username(new_name)
        self.username = new_name
        return new_name

    def generate_substitutions(self, viewer):
        return {
            "name": self.get_display_name(viewer),
            "email": self.email
        }

    def get_account(self):
        return self

    def characters(self):
        return AthanorPlayerCharacter.objects.filter_family(character_bridge__db_namespace=0,
                                                            character_bridge__db_account=self)

    def render_character_menu(self, cmd):
        """
        Displays the character menu for the Account's 'Look' command.

        Args:
            cmd (AthanorCommand): The running command for CmdOOCLook or etc.

        Returns:
            Display (str): What to display to the looker.
        """
        message = list()
        message.append(cmd.styled_header(f"Account: {self.username}"))
        message.append(f"|wEmail:|n {self.email}")
        if (sessions := self.sessions.all()):
            message.append(cmd.styled_separator("Sessions"))
            for sess in sessions:
                message.append(sess.render_character_menu_line(cmd))
        if (characters := self.characters()):
            message.append(cmd.styled_separator("Characters"))
            for char in characters:
                message.append(char.render_character_menu_line(cmd))
        caller_admin = cmd.caller.locks.check_lockstring(cmd.caller, "dummy:pperm(Admin)")
        message.append(cmd.styled_separator("Commands"))
        if not settings.RESTRICTED_CHARACTER_CREATION or caller_admin:
            message.append("|w@charcreate <name>|n to create a Character.")
        if not settings.RESTRICTED_CHARACTER_DELETION or caller_admin:
            message.append("|w@chardelete <name>=<verify name>|n to delete a character.")
        if not settings.RESTRICTED_CHARACTER_RENAME or caller_admin:
            message.append("|w@charrename <character>=<new name>|n to rename a character.")
        if not settings.RESTRICTED_ACCOUNT_RENAME or caller_admin:
            message.append("|w@username <name>|n to change your Account username.")
        if not settings.RESTRICTED_ACCOUNT_EMAIL or caller_admin:
            message.append("|w@email <new email>|n to change your Email")
        if not settings.RESTRICTED_ACCOUNT_PASSWORD or caller_admin:
            message.append("|w@password <old>=<new>|n to change your password.")
        message.append("|w@ic <name>|n to enter the game as a Character.")
        message.append("|w@ooc|n to return here again.")
        message.append("|whelp|n for more information.")
        message.append("|wQUIT|n to disconnect.")
        message.append(cmd._blank_footer)
        return '\n'.join(str(l) for l in message)
