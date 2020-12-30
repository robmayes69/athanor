import re
from collections import defaultdict

from django.conf import settings

from evennia.utils.utils import make_iter, time_format
from evennia.utils.search import search_account
from evennia.accounts.models import AccountDB

from athanor.utils.controllers import AthanorController, AthanorControllerBackend
from athanor.accounts.typeclasses import AthanorAccount
from athanor.accounts import messages as amsg
from athanor.utils.text import partial_match, iter_to_string
from athanor.utils.time import utcnow, duration_from_string
from athanor.identities.identities import AccountIdentity, CharacterIdentity
from athanor.identities.models import IdentityDB
from athanor.entities.characters import AthanorCharacter
from athanor.utils import error


class AthanorAccountController(AthanorController):
    system_name = 'ACCOUNTS'

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def create_account(self, session, username, email, password, typeclass=None, login_screen=False):
        enactor = None
        if not login_screen:
            if not (enactor := session.get_account()) or not enactor.check_lock("oper(account_create)"):
                raise error.PermissionException("Permission denied.")
        else:
            pass  #TODO: add in a section for limiting login screen Account creation...
        if not username:
            raise error.SyntaxException("An Account must have a username!")
        if not email:
            raise error.SyntaxException("An Account must have an email address!")
        if not password:
            raise error.SyntaxException("An Account must have a password!")
        new_account = self.backend.create_account(username, email, password, typeclass=typeclass)
        entities = {'enactor': enactor if enactor else session, 'account': new_account}
        if login_screen:
            amsg.CreateMessage(entities).send()
        else:
            amsg.CreateMessageAdmin(entities, password=password).send()
        return new_account

    def rename_account(self, session, account, new_name, ignore_priv=False):
        if not (enactor := session.get_account()) or (not ignore_priv and not enactor.check_lock("pperm(Admin)")):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        old_name, new_name = self.backend.rename_account(account, new_name)
        entities = {'enactor': enactor, 'account': account}
        amsg.RenameMessage(entities, old_name=old_name).send()

    def email_account(self, session, account, new_email, ignore_priv=False):
        if not (enactor := session.get_account()) or (not ignore_priv and not enactor.check_lock("pperm(Admin)")):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        old_email, new_email = self.backend.change_email(account, new_email)
        entities = {'enactor': enactor, 'account': account}
        amsg.EmailMessage(entities, old_email=old_email).send()

    def find_account(self, search_text, exact=False):
        return self.backend.find_account(search_text, exact=exact)

    find_user = find_account

    def disable_account(self, session, account, reason):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        if account.db._disabled:
            raise error.WrongStateException("Account is already disabled!")
        if not reason:
            raise error.SyntaxException("Must include a reason!")
        account.db._disabled = reason
        entities = {'enactor': enactor, 'account': account}
        amsg.DisableMessage(entities, reason=reason).send()
        account.force_disconnect(reason)

    def enable_account(self, session, account):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        if not account.db._disabled:
            raise error.WrongStateException("Account is not disabled!")
        del account.db._disabled
        entities = {'enactor': enactor, 'account': account}
        amsg.EnableMessage(entities).send()

    def ban_account(self, session, account, duration, reason):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Moderator)"):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        duration = duration_from_string(duration)
        ban_date = utcnow() + duration
        if not reason:
            raise error.SyntaxException("Must include a reason!")
        account.db._banned = ban_date
        account.db._ban_reason = reason
        entities = {'enactor': enactor, 'account': account}
        amsg.BanMessage(entities, duration=time_format(duration.total_seconds(), style=2),
                        ban_date=ban_date.strftime('%c'), reason=reason).send()
        account.force_disconnect(reason)

    def unban_account(self, session, account):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Moderator)"):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        if not ((banned := account.db._banned) and banned > utcnow()):
            raise error.WrongStateException("Account is not banned!")
        del account.db._banned
        del account.db._ban_reason
        entities = {'enactor': enactor, 'account': account}
        amsg.UnBanMessage(entities).send()

    def password_account(self, session, account, new_password, ignore_priv=False, old_password=None):
        if not (enactor := session.get_account()) or (not ignore_priv and not enactor.check_lock("oper(account_password)")):
            raise error.PermissionException("Permission denied.")
        if ignore_priv and not account.check_password(old_password):
            raise error.PermissionException("Permission denied. Password was incorrect.")
        account = self.find_account(account)
        if not new_password:
            raise error.BadInputException("Passwords may not be empty!")
        account.set_password(new_password)
        account.db._date_password_changed = utcnow()
        entities = {'enactor': enactor, 'account': account}
        if old_password:
            amsg.PasswordMessagePrivate(entities).send()
        else:
            amsg.PasswordMessageAdmin(entities, password=new_password).send()

    def disconnect_account(self, session, account, reason):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Moderator)"):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        if not account.sessions.all():
            raise error.WrongStateException("Account is not connected!")
        entities = {'enactor': enactor, 'account': account}
        amsg.ForceDisconnect(entities, reason=reason).send()
        account.force_disconnect(reason=reason)

    def find_permission(self, perm):
        if not perm:
            raise error.NoDataException("No permission entered!")
        if not (found := partial_match(perm, settings.PERMISSIONS.keys())):
            raise error.TargetNotFoundException("Permission not found!")
        return found

    def grant_permission(self, session, account, perm):
        if not (enactor := session.get_account()):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        perm = self.find_permission(perm)
        perm_data = settings.PERMISSIONS.get(perm, dict())
        perm_lock = perm_data.get("permission", None)
        if not perm_lock:
            if not enactor.is_superuser:
                raise error.PermissionException("Permission denied. Only a Superuser can grant this.")
        if perm_lock:
            passed = False
            for lock in make_iter(perm_lock):
                if (passed := enactor.check_lock(f"pperm({lock})")):
                    break
            if not passed:
                raise error.PermissionException(f"Permission denied. Requires {perm_lock} or better.")
        if perm.lower() in account.permissions.all():
            raise error.AthanorException(f"{account} already has that Permission!")
        account.permissions.add(perm)
        self.permissions[perm.lower()].add(account)
        entities = {'enactor': enactor, 'account': account}
        amsg.GrantMessage(entities, perm=perm).send()

    def revoke_permission(self, session, account, perm):
        if not (enactor := session.get_account()):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        perm = self.find_permission(perm)
        perm_data = settings.PERMISSIONS.get(perm, dict())
        perm_lock = perm_data.get("permission", None)
        if not perm_lock:
            if not enactor.is_superuser:
                raise error.PermissionException("Permission denied. Only a Superuser can grant this.")
        if perm_lock:
            passed = False
            for lock in make_iter(perm_lock):
                if (passed := enactor.check_lock(f"pperm({lock})")):
                    break
            if not passed:
                raise error.PermissionException(f"Permission denied. Requires {perm_lock} or better.")
        if perm.lower() not in account.permissions.all():
            raise error.NoDataException(f"{account} does not have that Permission!")
        account.permissions.remove(perm)
        self.permissions[perm.lower()].remove(account)
        entities = {'enactor': enactor, 'account': account}
        amsg.RevokeMessage(entities, perm=perm).send()

    def toggle_super(self, session, account):
        if not (enactor := session.get_account()) or not enactor.is_superuser:
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        acc_super = account.is_superuser
        reverse = not acc_super
        entities = {'enactor': enactor, 'account': account}
        if acc_super:
            amsg.RevokeSuperMessage(entities).send()
        else:
            amsg.GrantSuperMessage(entities).send()
        account.is_superuser = reverse
        account.save(update_fields=['is_superuser'])
        if reverse:
            self.permissions["_super"].add(account)
        else:
            self.permissions["_super"].remove(account)
        return reverse

    def access_account(self, session, account):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        styling = enactor.styler
        message = list()
        message.append(styling.styled_header(f"Access Levels: {account}"))
        message.append(f"PERMISSION HIERARCHY: {iter_to_string(settings.PERMISSION_HIERARCHY)} <<<< SUPERUSER")
        message.append(f"HELD PERMISSIONS: {iter_to_string(account.permissions.all())} ; SUPERUSER: {account.is_superuser}")
        message.append(styling.blank_footer)
        return '\n'.join(str(l) for l in message)

    def permissions_directory(self, session):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise error.PermissionException("Permission denied.")
        # Create a COPY of the permissions since we're going to mutilate it a lot...

        perms = dict(self.permissions)
        message = list()
        styling = enactor.styler
        message.append(styling.styled_header("Permissions Hierarchy"))
        message.append(f"|rSUPERUSERS:|n {iter_to_string(perms.pop('_super', list()))}")
        for perm in reversed(settings.PERMISSION_HIERARCHY):
            if perm.lower() in perms:
                message.append(f"{perm:>10}: {iter_to_string(perms.pop(perm.lower(), list()))}")
        if perms:
            message.append(styling.styled_separator("Non-Hierarchial Permissions"))
            for perm, holders in perms.items():
                if not holders:
                    continue
                message.append(f"{perm}: {iter_to_string(holders)}")
        message.append(styling.blank_footer)
        return '\n'.join(str(l) for l in message)

    def list_permissions(self, session):
        if not (enactor := session.get_account()):
            raise error.PermissionException("Permission denied.")
        styling = enactor.styler
        message = list()
        message.append(styling.styled_header("Grantable Permissions"))
        for perm, data in settings.PERMISSIONS.items():
            message.append(styling.styled_separator(perm))
            message.append(f"Grantable By: {data.get('permission', 'SUPERUSER')}")
            if (desc := data.get("description", None)):
                message.append(f"Description: {desc}")
        message.append(styling.blank_footer)
        return '\n'.join(str(l) for l in message)

    def list_accounts(self, session):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise error.PermissionException("Permission denied.")
        if not (accounts := AthanorAccount.objects.filter_family()):
            raise error.NoDataException("No accounts to list!")
        styling = enactor.styler
        message = [
            styling.styled_header(f"Account Listing")
        ]
        for acc in accounts:
            message.extend(acc.render_list_section(enactor, styling))
        message.append(styling.blank_footer)
        return '\n'.join(str(l) for l in message)

    def examine_account(self, session, account):
        if not (enactor := session.get_account()) or not enactor.check_lock("pperm(Admin)"):
            raise error.PermissionException("Permission denied.")
        account = self.find_account(account)
        return account.render_examine(enactor)

    def all(self):
        return self.backend.all()

    def count(self):
        return self.backend.count()

    def integrity_check(self):
        self.backend.integrity_check()

    def create_character(self, session, account, name, typeclass=None, select_screen=True, **kwargs):
        enactor = None
        if not select_screen:
            if not (enactor := session.get_account()) or not enactor.check_lock("oper(character_create)"):
                raise error.PermissionException("Permission denied.")
        if not name:
            raise error.SyntaxException("A Character must have a name!")
        new_character = self.backend.create_character(account, name, typeclass=typeclass, select_screen=select_screen, **kwargs)
        entities = {'enactor': enactor if enactor else session, 'character': new_character}
        if select_screen:
            amsg.CreateMessage(entities).send()
        else:
            amsg.CreateMessageAdmin(entities).send()
        return new_character


class AthanorAccountControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('account_typeclass', 'BASE_ACCOUNT_TYPECLASS', AthanorAccount),
        ('account_identity', 'BASE_ACCOUNT_IDENTITY_TYPECLASS', AccountIdentity),
        ('character_typeclass', 'BASE_CHARACTER_TYPECLASS', AthanorCharacter),
        ('character_identity', 'BASE_CHARACTER_IDENTITY_TYPECLASS', CharacterIdentity)
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.id_map = dict()
        self.name_map = dict()
        self.roles = dict()
        self.reg_names = None
        self.account_typeclass = None
        self.account_identity = None
        self.character_typeclass = None
        self.character_identity = None
        self.permissions = defaultdict(set)
        self.load()

    def integrity_check(self):
        c_type = self.account_typeclass.get_concrete_content_type()
        for acc in self.all():
            if not (found := IdentityDB.objects.filter(content_type=c_type, object_id=acc.id).first()):
                # no Identity for this Account... so we'll create one.
                identity = self.account_identity.create(acc.username, wrapped=acc)

    def all(self):
        return AccountDB.objects.all()

    def count(self):
        return AccountDB.objects.count()

    def create_account(self, username, email, password, typeclass=None):
        if typeclass is None:
            typeclass = self.account_typeclass
        new_account = typeclass.create_account(username=username, email=email, password=password)
        self.id_map[new_account.id] = new_account
        self.name_map[new_account.username.upper()] = new_account
        self.update_regex()
        for perm in new_account.permissions.all():
            self.permissions[perm].add(new_account)
        return new_account

    def update_regex(self):
        escape_names = [re.escape(name) for name in self.name_map.keys()]
        self.reg_names = re.compile(r"(?i)\b(?P<found>%s)\b" % '|'.join(escape_names))

    def update_cache(self):
        accounts = AthanorAccount.objects.filter_family()
        self.id_map = {acc.id: acc for acc in accounts}
        self.name_map = {acc.username.upper(): acc for acc in accounts}
        self.update_regex()
        self.permissions = defaultdict(set)
        for acc in accounts:
            for perm in acc.permissions.all():
                self.permissions[perm].add(acc)
            if acc.is_superuser:
                self.permissions["_super"].add(acc)

    def rename_account(self, account, new_name):
        old_name = str(account)
        new_name = account.rename(new_name)
        return old_name, new_name

    def change_email(self, account, new_email):
        old_email = account.email
        new_email = account.set_email(new_email)
        return old_email, new_email

    def find_account(self, search_text, exact=False):
        if not search_text:
            raise error.SyntaxException("No account entered to search for!")
        if isinstance(search_text, AthanorAccount):
            return search_text
        if '@' in search_text:
            found = AthanorAccount.objects.get_account_from_email(search_text).first()
            if found:
                return found
            raise error.TargetNotFoundException(f"Cannot find a user with email address: {search_text}")
        found = search_account(search_text, exact=exact)
        if len(found) == 1:
            return found[0]
        if not found:
            raise error.TargetNotFoundException(f"Cannot find a user named {search_text}!")
        raise error.TargetAmbiguousException(f"That matched multiple accounts: {found}")

    def create_character(self, account, name, typeclass=None, login_screen=False, **kwargs):
        if typeclass is None:
            typeclass = self.character_typeclass
        new_char = typeclass.create_character(name, account=account, login_screen=login_screen,
                                              identity_typeclass=self.character_identity, **kwargs)
        return new_char
