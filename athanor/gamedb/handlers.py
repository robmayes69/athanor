from django.conf import settings
from evennia.utils.utils import delay

import athanor


class PrivilegeHandler(object):

    def __init__(self, owner, mode):
        self.owner = owner
        self.cached_answers = dict()
        self.mode = mode
        self.lower_mode = mode.lower()

    def check(self, privilege):
        if (found := self.cached_answers.get(privilege, None)) is not None:
            return found
        priv_data = settings.PRIVILEGES[self.mode].get(privilege, dict())
        if not priv_data:
            return False
        priv_perm = priv_data.get("permission", "Developer")
        if self.owner.locks.check_lockstring(self.owner, f'dummy:pperm({priv_perm})'):
            self.cached_answers[privilege] = True
            return True
        all_roles = self.owner.roles.all()
        for role_key, role_def in athanor.CONTROLLER_MANAGER.get(self.lower_mode).roles.items():
            if role_key not in all_roles:
                continue
            if privilege in role_def.get('privileges', set()):
                self.cached_answers[privilege] = True
                return True
        self.cached_answers[privilege] = False
        return False

    def all(self):
        if len(self.cached_answers.keys()) != len(settings.PRIVILEGES[self.mode]):
            for priv in settings.PRIVILEGES[self.mode].keys():
                self.check(priv)
        return {priv_key: priv_result for priv_key, priv_result in self.cached_answers.items() if priv_result}.keys()

    def clear_cache(self):
        return self.cached_answers.clear()


class RoleHandler(object):

    def __init__(self, owner):
        self.owner = owner
        if not self.owner.attributes.has(key='roles'):
            self.owner.attributes.add(key='roles', value=set())
        self.roles = self.owner.attributes.get(key='roles')

    def add(self, role):
        if role in self.roles:
            return
        self.roles.add(role)
        self.owner.privileges.clear_cache()

    def remove(self, role):
        if role not in self.roles:
            return
        self.roles.remove(role)
        self.owner.privileges.clear_cache()

    def all(self):
        return set(self.roles)
