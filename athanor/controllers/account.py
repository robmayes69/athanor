from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from evennia.utils.search import search_account

from athanor.gamedb.scripts import AthanorGlobalScript
from athanor.gamedb.accounts import AthanorAccount


class AthanorAccountController(AthanorGlobalScript):
    system_name = 'ACCOUNTS'

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.account_typeclass = class_from_module(settings.BASE_ACCOUNT_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.account_typeclass = AthanorAccount

    def create_account(self, session, username, email, password, show_password=False):
        new_account = self.ndb.account_typeclass.create_account(username=username, email=email, password=password)
        if not isinstance(new_account.db._playable_characters, list):
            new_account.db._playable_characters = list()
        return new_account

    def rename_account(self, session, account, new_name):
        pass

    def change_email(self, session, account, new_email):
        pass

    def find_account(self, search_text, exact=False):
        if isinstance(search_text, AthanorAccount):
            return search_text
        if '@' in search_text:
            found = DefaultAccount.objects.get_account_from_email(search_text).first()
            if found:
                return found
            raise ValueError(f"Cannot find a user with email address: {search_text}")
        found = search_account(search_text, exact=exact)
        if len(found) == 1:
            return found[0]
        if not found:
            raise ValueError(f"Cannot find a user named {search_text}!")
        raise ValueError(f"That matched multiple accounts: {found}")

    def disable_account(self, session, account):
        pass

    def enable_account(self, session, account):
        pass

    def ban_account(self, session, account, duration):
        pass
