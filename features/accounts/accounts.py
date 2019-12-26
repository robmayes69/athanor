from evennia.abstracts.accounts import DefaultAccount, DefaultGuest
from features.core.base import AthanorEntity
from typeclasses.scripts import GlobalScript
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from evennia.utils.search import search_account
import datetime
from features.core.menu import AthanorMenu


class AccountMixin(object):

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

    def is_banned(self):
        return False

    def is_disabled(self):
        return False


class AthanorAccount(DefaultAccount, AccountMixin, AthanorEntity):

    def __init__(self, *args, **kwargs):
        DefaultAccount.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)

    def __str__(self):
        return self.key


class AthanorGuest(DefaultGuest, AccountMixin, AthanorEntity):

    def __init__(self, *args, **kwargs):
        DefaultGuest.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)


class DefaultAccountController(GlobalScript):
    system_name = 'ACCOUNTS'

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.account_typeclass = class_from_module(settings.BASE_ACCOUNT_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.account_typeclass = AthanorAccount

    def all(self):
        return DefaultAccount.objects.filter_family()

    def search_name(self, name):
        return self.all().filter(username__istartswith=name)

    def search_email(self, email):
        return self.all().filter(email__istartswith=email)

    def create_account(self, session, username, email, password, show_password=False):
        new_account, errors = self.ndb.account_typeclass.create(username=username, email=email, password=password)
        if errors:
            raise ValueError(f"Error Creating {username} - {email}: {str(errors)}")
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

    def add_permission(self, session, account, permission):
        pass

    def rem_permission(self, session, account, permission):
        pass

    def toggle_superuser(self, session, account):
        pass

    def menu_create(self, session, caller):
        AthanorMenu(caller, 'features.accounts.menu_admin', startnode='node_main', session=session,
                    menu_name='Account System')

    def menu_edit(self, session, caller, start_target=None):
        AthanorMenu(caller, 'features.accounts.menu_admin', startnode='node_edit', session=session, menu_name='Account System', start_target=start_target)


    def menu_search(self, session, caller):
        AthanorMenu(caller, 'features.accounts.menu_admin', startnode='node_search', session=session,
                    menu_name='Account System')