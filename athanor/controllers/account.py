from evennia import GLOBAL_SCRIPTS
from django.conf import settings

from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from evennia.utils.search import search_account

from athanor.gamedb.scripts import AthanorGlobalScript
from athanor.gamedb.accounts import AthanorAccount

MIXINS = [class_from_module(mixin) for mixin in settings.CONTROLLER_MIXINS["ACCOUNT"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorAccountController(*MIXINS, AthanorGlobalScript):
    system_name = 'ACCOUNTS'

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.account_typeclass = class_from_module(settings.BASE_ACCOUNT_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.account_typeclass = AthanorAccount

        self.update_cache()
        self.update_roles()

    def update_cache(self):
        accounts = AthanorAccount.objects.filter_family()
        self.ndb.id_map = {acc.id: acc for acc in accounts}
        self.ndb.name_map = {acc.username.upper(): acc for acc in accounts}

    def update_roles(self):
        self.ndb.roles = dict()
        for plugin in GLOBAL_SCRIPTS.gamedata.ndb.plugins_sorted:
            self.ndb.roles.update(plugin.data.get("roles", dict()))

    def create_account(self, session, username, email, password, show_password=False, login_screen=False, **kwargs):
        if not login_screen:
            if not (enactor := session.get_account()) or not enactor.privileges.check("account_create"):
                raise ValueError("Permission denied.")
        new_account = self.ndb.account_typeclass.create_account(username=username, email=email, password=password,
                                                                **kwargs)
        self.ndb.id_map[new_account.id] = new_account
        self.ndb.name_map[new_account.username.upper()] = new_account
        return new_account

    def rename_account(self, session, account, new_name):
        if not (enactor := session.get_account()) or not enactor.privileges.check("account_rename"):
            raise ValueError("Permission denied.")
        account = self.find_account(account)
        old_name = str(account)
        account.rename(new_name)

    def change_email(self, session, account, new_email):
        if not (enactor := session.get_account()) or not enactor.privileges.check("account_email"):
            raise ValueError("Permission denied.")
        account = self.find_account(account)
        old_email = account.email
        account.change_email(new_email)

    def find_account(self, search_text, exact=False):
        if isinstance(search_text, AthanorAccount):
            return search_text
        if '@' in search_text:
            found = AthanorAccount.objects.get_account_from_email(search_text).first()
            if found:
                return found
            raise ValueError(f"Cannot find a user with email address: {search_text}")
        found = search_account(search_text, exact=exact)
        if len(found) == 1:
            return found[0]
        if not found:
            raise ValueError(f"Cannot find a user named {search_text}!")
        raise ValueError(f"That matched multiple accounts: {found}")

    def disable_account(self, session, account, reason):
        if not (enactor := session.get_account()) or not enactor.privileges.check("account_disable"):
            raise ValueError("Permission denied.")
        account = self.find_account(account)

    def enable_account(self, session, account, reason):
        if not (enactor := session.get_account()) or not enactor.privileges.check("account_disable"):
            raise ValueError("Permission denied.")
        account = self.find_account(account)

    def ban_account(self, session, account, duration):
        if not (enactor := session.get_account()) or not enactor.privileges.check("account_ban"):
            raise ValueError("Permission denied.")
        account = self.find_account(account)

    def unban_account(self, session, account):
        if not (enactor := session.get_account()) or not enactor.privileges.check("account_ban"):
            raise ValueError("Permission denied.")
        account = self.find_account(account)

    def reset_password(self, session, account, new_password):
        if not (enactor := session.get_account()) or not enactor.privileges.check("account_password"):
            raise ValueError("Permission denied.")
        account = self.find_account(account)

    def grant_role(self, session, account, role_key):
        pass

    def revoke_role(self, session, account, role_key):
        pass
