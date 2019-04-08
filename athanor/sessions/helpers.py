import math
from evennia.utils.ansi import ANSIString
from evennia.utils import evtable
import athanor
from athanor.base.helpers import SessionBaseHelper


class SessionCoreHelper(SessionBaseHelper):
    key = 'core'
    style = 'fallback'
    system_name = 'SYSTEM'
    operations = ('create_account', 'create_character', 'set_account_disabled', 'set_character_disabled',
                  'set_account_banned', 'set_character_banned', 'set_character_shelved', 'login_account',
                  'puppet_character')
    cmdsets = ('athanor.sessions.unlogged.UnloggedCmdSet',)

    def at_sync(self):
        if not self.owner.logged_in:
            for cmdset in self.cmdsets:
                self.owner.cmdset.add(cmdset)

    def at_login(self, account, **kwargs):
        for cmdset in self.cmdsets:
            self.owner.cmdset.remove(cmdset)

    def is_builder(self):
        if not self.owner.account:
            return False
        return self.owner.account.ath['core'].is_builder()

    def is_admin(self):
        if not self.owner.account:
            return False
        return self.owner.account.ath['core'].is_admin()

    def is_developer(self):
        if not self.owner.account:
            return False
        return self.owner.account.ath['core'].is_developer()

    def is_superuser(self):
        if not self.owner.account:
            return False
        return self.owner.account.is_superuser

    def permission_rank(self):
        if not self.owner.account:
            return 0
        return self.owner.account.ath['core'].permission_rank()

    def can_modify(self, target):
        if not self.permission_rank() > 2:
            return False
        return self.permission_rank() > target.ath['core'].permission_rank()


class SessionRendererHelper(SessionBaseHelper):
    key = 'render'

