import datetime

from django.db import transaction
from django.conf import settings

from evennia.accounts.accounts import DefaultAccount
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from evennia.utils.search import search_account

from athanor.core.objects import AthanorObject
from athanor.core.models import AccountBridge
from athanor.core.gameentity import AthanorGameEntity
from athanor.core.scripts import AthanorGlobalScript


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


class AthanorAccount(DefaultAccount, AccountMixin, AthanorGameEntity):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        return self.key

    def create_bridge(self):
        """
        Called by create_account and at_intial_setup to create an Account Bridge Object.
        Meant to be called within a transaction.

        Returns:
            None
        """
        if hasattr(self, 'account_bridge'):
            return
        acc_bridge_typeclass = class_from_module(settings.ACCOUNT_BRIDGE_OBJECT_TYPECLASS)
        obj, errors = acc_bridge_typeclass.create_account_bridge(account=self)
        bridge, created = AccountBridge.objects.get_or_create(db_account=self, db_object=obj)
        if created:
            bridge.save()

    @classmethod
    def create_account(cls, *args, **kwargs):
        account, errors = cls.create(*args, **kwargs)
        account.create_bridge()
        return account, errors


class AthanorAccountBridge(AthanorObject):

    @classmethod
    def create_account_bridge(cls, account):
        obj, errors = cls.create(account.key, account)
        return obj, errors


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
        new_account, errors = self.ndb.account_typeclass.create_account(username=username, email=email, password=password)
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
