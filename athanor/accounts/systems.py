from django.db.models import Q
from django.contrib.auth import authenticate
from athanor.accounts.classes import Account
from evennia.utils.create import create_account
from athanor import AthException
from athanor.base.systems import AthanorSystem
from athanor.utils.text import partial_match
from athanor.utils.online import accounts as on_accounts
from athanor.utils.time import utcnow

PERMISSIONS_DICT = {
    5: ('Superuser', 'Developer', 'Admin', 'Builder', 'Helper'),
    4: ('Admin', 'Builder', 'Helper'),
    3: ('Builder', 'Helper')
}


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
    run_interval = 60

    def load(self):
        results = Account.objects.filter_family().values_list('id', 'username', 'email')
        self.ndb.name_map = {q[1].upper(): q[0] for q in results}
        self.ndb.email_map = {q[2].upper(): q[0] for q in results}
        self.ndb.id_map = {q[0]: q[1] for q in results}
        self.ndb.online_accounts = set(on_accounts())

    def search(self, session, find):
        if not find:
            raise AthException("Must enter search terms!")
        if find.lower() in ('self', 'me') and hasattr(session, 'account'):
            return session.account
        if find.isdigit():
            results = Account.objects.filter_family(id=find).first()
        else:
            results = Account.objects.filter_family(Q(username__iexact=find) | Q(email__iexact=find)).first()
        if results:
            return results
        results = Account.objects.filter_family(username_istartswith=find).order_by('username')
        if results.count() > 1 and session.ath['core'].is_admin:
            raise AthException("Account Search Ambiguous. Matched: %s" % ', '.join(results))
        if not results:
            raise AthException("Account not found!")
        return results.first()

    def create(self, session, name, password, email=None, method=None):
        name = self.valid['account_name'](session, name)
        password = self.valid['account_password'](session, password)
        if email:
            email = self.valid['account_email'](session, email)
        new_account = create_account(name, email, password)
        self.alert("Created Account '%s' - Method: %s" % (new_account, method), source=session)
        return new_account

    def all(self, session):
        if not session.ath['core'].is_admin():
            raise AthException("Permission denied.")
        return Account.objects.filter_family().order_by('db_key')

    def delete(self, session, account):
        if not session.ath['core'].is_admin():
            raise AthException("Permission denied.")
        account = self.valid['account'](session, account)
        if not session.account.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        account.delete()

    def rename(self, session, account, new_name):
        account = self.valid['account'](session, account)
        if not session.account.ath['core'].can_modify(account) and not (hasattr(session, 'account') and session.account == account and self['rename_self']):
            raise AthException("Permission denied.")
        new_name = self.valid['account_name'](session, new_name, rename_from=account)
        old_name = account.key
        old_account = str(account)
        account.key = new_name
        account.ath['core'].alert("Your Account has been renamed from %s to: %s" % (old_name, new_name))
        self.alert("Renamed Account '%s' to: %s" % (old_account, account), source=session)
        return account, old_name

    def email(self, session, account, new_email):
        account = self.valid['account'](session, account)
        if not session.account.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        new_email = self.valid['account_email'](session, new_email)
        old_email = account.email
        account.ath['core'].alert("Your Email has been changed from %s to: %s" % (old_email, new_email))
        self.alert("Changed Account '%s' Email from %s to: %s" % (account, old_email, new_email), source=session)
        account.email = new_email
        return account, new_email

    def get(self, session, account):
        account = self.valid['account'](session, account)
        return account

    def disable(self, session, account):
        account = self.valid['account'](session, account)
        if session.account == account:
            raise AthException("Cannot disable yourself!")
        if not session.account.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        account.ath['core'].alert("Your Account has been disabled!")
        account.ath['core'].disabled = True
        self.alert("Disabled Account '%s'" % account, source=session)
        return account

    def enable(self, session, account):
        account = self.valid['account'](session, account)
        if not session.account.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        account.ath['core'].alert("Your Account has been enabled!")
        account.ath['core'].disabled = False
        self.alert("Enabled Account '%s'" % account, source=session)
        return account

    def ban(self, session, account, duration):
        account = self.valid['account'](session, account)
        if session.account == account:
            raise AthException("Cannot ban yourself!")
        if not session.account.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        duration = self.valid['duration'](session, duration)
        until = utcnow() + duration
        account.ath['core'].alert("Your Account has been banned for %s!" % duration)
        account.ath['core'].banned = until
        self.alert("Banned Account '%s' for %s - Until %s" % (account, duration, until), source=session)
        return account, duration, until

    def unban(self, session, account):
        account = self.valid['account'](session, account)
        if not session.account.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        account.ath['core'].alert("Your Account has been unbanned!")
        account.ath['core'].banned = False
        self.alert("Enabled Account '%s'" % account, source=session)
        return account

    def at_repeat(self):
        for acc in self.ndb.online_accounts:
            acc.ath['core'].update_playtime(self.interval)

    def add_online(self, account):
        self.ndb.online_accounts.add(account)

    def remove_online(self, account):
        self.ndb.online_accounts.remove(account)

    def password(self, session, account, new_password):
        account = self.valid['account'](session, account)
        if not session.account.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        new_password = self.valid['account_password'](session, new_password)
        account.set_password(new_password)
        if session.account != account:
            self.alert("Password for Account '%s' was changed!" % account, source=session)
            account.ath['core'].alert("Your password has been changed!")
        return account

    def grant(self, session, account, permission):
        account = self.valid['account'](session, account)
        if session.account == account:
            raise AthException("Cannot modify your own account!")
        available = PERMISSIONS_DICT.get(session.ath['core'].permission_rank(),None)
        if not available:
            raise AthException("Insufficient permissions to grant any privileges!")
        if not session.account.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        permission = partial_match(permission, available)
        if not permission:
            raise AthException("Permission not found!")
        if permission == 'Superuser':
            if account.is_superuser:
                raise AthException("Account '%s' is already a Superuser!" % account)
            account.is_superuser = True
        else:
            if permission.lower() in account.permissions.all():
                raise AthException("Account '%s' already possesses Permission: %s" % (account, permission))
            account.permissions.add(permission.lower())
        account.ath['core'].alert("Your Account has been Granted Permission: %s" % permission)
        self.alert("Granted Account '%s' Permission: %s" % (account, permission))
        return account, permission

    def revoke(self, session, account, permission):
        account = self.valid['account'](session, account)
        if session.account == account:
            raise AthException("Cannot modify your own account!")
        available = PERMISSIONS_DICT.get(session.ath['core'].permission_rank(), None)
        if not available:
            raise AthException("Insufficient permissions to revoke any privileges!")
        if not session.account.ath['core'].can_modify(account):
            raise AthException("Permission denied.")
        permission = partial_match(permission, available)
        if not permission:
            raise AthException("Permission not found!")
        if permission == 'Superuser':
            if not account.is_superuser:
                raise AthException("Account '%s' is not a Superuser!" % account)
            account.is_superuser = False
        else:
            if not permission.lower() in account.permissions.all():
                raise AthException("Account '%s' does not have Permission: %s" % (account, permission))
            account.permissions.remove(permission.lower())
        account.ath['core'].alert("Your Account has lost Permission: %s" % permission)
        self.alert("Revoked Account '%s' Permission: %s" % (account, permission))
        return account, permission

    def login(self, session, account, password):
        if session.account:
            raise AthException("You are already logged in!")
        account = self.valid['account'](session, account)
        if not len(password):
            raise AthException("You must enter a password!")
        auth_account = authenticate(username=account.username, password=password)
        if not auth_account:
            account.at_failed_login(session)
            raise AthException("Invalid password!")
        session.sessionhandler.login(session, account)
