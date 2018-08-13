from athanor.accounts.classes import Account
from evennia.utils.create import create_account
from athanor import AthException
from athanor.base.systems import AthanorSystem
from athanor.utils.online import accounts as on_accounts


class AccountSystem(AthanorSystem):
    key = 'account'
    system_name = 'ACCOUNT'
    load_order = -999
    settings_data = (
    ('rename_self', 'Can users rename their own accounts?', 'boolean', True),
    ('unique_email', 'Email addresses cannot be duplicated across accounts.', 'boolean', True),
    ('email_self', "Can users change their own email addresses?", 'boolean', True)
    )
    start_delay = True
    interval = 60

    def load(self):
        results = Account.objects.filter_family().values_list('id', 'username', 'email')
        self.ndb.name_map = {q[1].upper(): q[0] for q in results}
        self.ndb.email_map = {q[2].upper(): q[0] for q in results}
        self.ndb.id_map = {q[0]: q[1] for q in results}

    def create(self, session, name, password, email=None, method=None):
        name = self.valid['account_name'](session, name)
        password = self.valid['account_password'](session, password)
        if email:
            email = self.valid['account_email'](session, email)
        new_account = create_account(name, email, password)
        return new_account

    def all(self, session):
        if not session.ath['core'].is_admin():
            raise AthException("Permission denied.")
        return Account.objects.filter_family().order_by('db_key')

    def delete(self, session, account):
        if not session.ath['core'].is_admin():
            raise AthException("Permission denied.")
        account = self.valid['account'](session, account)
        if not session.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        account.delete()

    def rename(self, session, account, new_name):
        account = self.valid['account'](session, account)
        if not session.ath['core'].can_modify(account) and not (hasattr(session, 'account') and session.account == account and self['rename_self']):
            raise AthException("Permission denied.")
        new_name = self.valid['account_name'](session, new_name, rename_from=account)
        old_name = account.key
        account.key = new_name

    def email(self, session, account, new_email):
        account = self.valid['account'](session, account)
        if not session.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        new_email = self.valid['account_email'](session, new_email)
        old_email = account.email
        account.email = new_email

    def get(self, session, account):
        account = self.valid['account'](session, account)
        return account

    def disable(self, session, account):
        pass

    def enable(self, session, account):
        pass

    def ban(self, session, account, duration):
        pass

    def unban(self, session, account):
        pass

    def at_start(self):
        self.ndb.online_accounts = set(on_accounts())

    def at_repeat(self):
        for acc in self.ndb.online_accounts:
            acc.ath['core'].update_playtime(self.interval)

    def add_online(self, account):
        self.ndb.online_accounts.add(account)

    def remove_online(self, account):
        self.ndb.online_accounts.remove(account)
