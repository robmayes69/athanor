from django.conf import settings
from evennia import GLOBAL_SCRIPTS


class RoleHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.cached_answers = dict()
        if not self.owner.attributes.has(key='roles'):
            self.owner.attributes.add(key='roles', value=set())
        self.roles = self.owner.attributes.get(key='roles')

    def access(self, privilege):
        if (found := self.cached_answers.get(privilege, None)) is not None:
            return found
        priv_data = settings.PRIVILEGES.get(privilege, dict())
        if not priv_data:
            return False
        priv_perm = priv_data.get("permission", "Developer")
        if self.owner.locks.check_lockstring('dummy', f'pperm({priv_perm})'):
            self.cached_answers[privilege] = True
            return True
        for role_key, role_def in GLOBAL_SCRIPTS.account.ndb.roles.items():
            if role_key not in self.roles:
                continue
            if privilege in role_def.get('privileges', set()):
                self.cached_answers[privilege] = True
                return True
        self.cached_answers[privilege] = False
        return False

    def add(self, role):
        self.roles.add(role)
        self.cached_answers.clear()

    def remove(self, role):
        self.roles.remove(role)
        self.cached_answers.clear()
