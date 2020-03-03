import datetime
from django.conf import settings

from evennia.utils.utils import class_from_module, lazy_property
from evennia.accounts.accounts import DefaultAccount
from evennia.utils import utils
from evennia.commands.cmdhandler import get_and_merge_cmdsets
from evennia import SESSION_HANDLER

import athanor

from athanor.utils.events import EventEmitter
from athanor.gamedb.characters import AthanorPlayerCharacter
from athanor.gamedb.base import HasRenderExamine
from athanor.utils.mixins import HasAttributeGetCreate

MIXINS = [class_from_module(mixin) for mixin in settings.GAMEDB_MIXINS["ACCOUNT"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorAccount(*MIXINS, HasAttributeGetCreate, HasRenderExamine, EventEmitter, DefaultAccount):
    """
    AthanorAccount adds the EventEmitter to DefaultAccount and supports Mixins.
    Please read Evennia's documentation for its normal API.

    Triggers Global Events:
        account_connect (session): Fired whenever a Session authenticates to this account.
        account_disconnect (session): Triggered whenever a Session disconnects from this account.
        account_online (session): Fired whenever an account comes online from being completely offline.
        account_offline (session): Triggered when an account's final session closes.
    """
    # class properties used by the RenderExamine mixin.
    examine_type = "account"
    examine_caller_type = "account"
    dbtype = 'AccountDB'

    def set_email(self, new_email):
        """
        Validates and normalizes email, then sets it.

        No permission checks are done here. That's on the Account Controller.

        Args:
            new_email (str): The new email.

        Returns:
            normalized_email (str)
        """
        if not new_email:
            raise ValueError("Must set an email address!")
        new_email = AthanorAccount.objects.normalize_email(new_email)
        if AthanorAccount.objects.filter_family(email__iexact=new_email).exclude(id=self.id).count():
            raise ValueError("This email address is already in use!")
        self.email = new_email
        self.save(update_fields=['email'])
        return new_email

    def render_examine(self, viewer, callback=True):
        obj_session = self.sessions.get()[0] if self.sessions.count() else None
        get_and_merge_cmdsets(
            self, obj_session, self, None, self.examine_type, "examine"
        ).addCallback(self.render_examine_callback, viewer)

    def render_examine_account(self, viewer, cmdset, styling):
        message = list()
        message.append(f"|wUsername|n: |c{self.name}|n ({self.dbref})")
        message.append(f"|wTypeclass|n: {self.typename} ({self.typeclass_path})")
        if (aliases := self.aliases.all()):
            message.append(f"|wAliases|n: {', '.join(utils.make_iter(str(aliases)))}")
        if (sessions := self.sessions.all()):
            message.append(f"|wSessions|n: {', '.join(str(sess) for sess in sessions)}")
        message.append(f"|wEmail|n: {self.email}")
        if (characters := self.characters()):
            message.append(f"|wCharacters|n: {', '.join(str(l) for l in characters)}")
        return message

    def render_examine_access(self, viewer, cmdset, styling):
        locks = str(self.locks)
        if locks:
            locks_string = utils.fill("; ".join([lock for lock in locks.split(";")]), indent=6)
        else:
            locks_string = " Default"
        message = [
            styling.styled_separator("Access"),
            f"|wPermissions|n: {', '.join(perms) if (perms := self.permissions.all()) else '<None>'}",
            f"|wSuperuser|n: {self.is_superuser}",
            f"|wLocks|n:{locks_string}"
        ]
        return message

    def render_examine_puppets(self, viewer, cmdset, styling):
        return list()

    def render_examine_puppeteer(self, viewer, cmdset, styling):
        message = [
            styling.styled_separator("Connected Account"),
            f"|wUsername|n: {self.username}",
            f"|wEmail|n: {self.email}",
            f"|wTypeclass|n: {self.typename} ({self.typeclass_path})",
            f"|wPermissions|n: {', '.join(perms) if (perms := self.permissions.all()) else '<None>'} (Superuser: {self.is_superuser}) (Quelled: {bool(self.db._quell)})",
            f"|wOperations|n: {', '.join(opers) if (opers := self.operations.all()) else '<None>'}",
            f"|wSessions|n: {', '.join(str(sess) for sess in self.sessions.all())}"
        ]
        return message

    def system_msg(self, text=None, system_name=None, enactor=None):
        sysmsg_border = self.options.sys_msg_border
        sysmsg_text = self.options.sys_msg_text
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def receive_template_message(self, text, msgobj, target):
        self.system_msg(text=text, system_name=msgobj.system_name)

    def render_list_section(self, enactor, styling):
        """
        Called by AccountController's list_accounts method. Renders this account
        on the list.
        """
        return [
            styling.styled_separator(self.username),
            f"|wEmail|n: {self.email}",
            f"|wLast Login|n: Last login here!",
            f"|wPermissions|n: {', '.join(self.permissions.all())} (Superuser: {self.is_superuser})",
            f"|wCharacters|n: {', '.join(str(c) for c in self.characters())}"
        ]

    def __str__(self):
        return self.key

    @classmethod
    def create_account(cls, *args, **kwargs):
        if not (email := kwargs.get('email', '')):
            raise ValueError("Must include an email!")
        if AthanorAccount.objects.filter_family(email__iexact=email).count():
            raise ValueError("Email is already in use by another account!")
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

    def rename(self, new_name):
        new_name = self.normalize_username(new_name)
        self.username = new_name
        self.save(update_fields=['username'])
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

    @lazy_property
    def styler(self):
        return athanor.STYLER(self)

    @lazy_property
    def colorizer(self):
        return self.get_or_create_attribute('colorizer', default=dict())

    def at_look(self, target=None, session=None, **kwargs):
        """
        Displays the character menu for the Account's 'Look' command.

        Args:
            cmd (AthanorCommand): The running command for CmdOOCLook or etc.

        Returns:
            Display (str): What to display to the looker.
        """
        styling = self.styler
        viewer = kwargs.pop('viewer', self)
        message = list()
        message.append(styling.styled_header(f"Account: {self.username}"))
        message.append(f"|wEmail:|n {self.email}")
        if (sessions := self.sessions.all()):
            message.append(styling.styled_separator("Sessions"))
            for sess in sessions:
                message.append(sess.render_character_menu_line(viewer))
        if (characters := self.characters()):
            message.append(styling.styled_separator("Characters"))
            for char in characters:
                message.append(char.render_character_menu_line(viewer))
        caller_admin = viewer.check_lock("pperm(Admin)")
        message.append(styling.styled_separator(viewer, "Commands"))
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
        message.append(styling.blank_footer)
        return '\n'.join(str(l) for l in message)

    def check_lock(self, lock):
        return self.locks.check_lockstring(self, f"dummy:{lock}")

    def force_disconnect(self, reason=""):
        """
        Forces a disconnect. This unpuppets all objects and disconnects all
        relevant sessions.

        Args:
            reason (str): If provided, will show this message to the Account.

        Returns:
            None
        """
        self.unpuppet_all()
        for sess in self.sessions.all():
            SESSION_HANDLER.disconnect(sess, reason=reason)
