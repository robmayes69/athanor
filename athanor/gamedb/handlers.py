from django.conf import settings

import athanor


class OperationHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.cached_answers = dict()

    def check(self, privilege):
        if (found := self.cached_answers.get(privilege, None)) is not None:
            return found
        op_data = settings.OPERATIONS.get(privilege, dict())
        if not op_data:
            return False
        op_perm = op_data.get("permission", "Developer")
        if self.owner.locks.check_lockstring(self.owner, f'dummy:pperm({op_perm})'):
            self.cached_answers[privilege] = True
            return True
        all_roles = self.owner.roles.all()
        for role_key, role_def in athanor.CONTROLLER_MANAGER.get('account').roles.items():
            if role_key not in all_roles:
                continue
            if privilege in role_def.get('privileges', set()):
                self.cached_answers[privilege] = True
                return True
        self.cached_answers[privilege] = False
        return False

    def all(self):
        if len(self.cached_answers.keys()) != len(settings.OPERATIONS):
            for priv in settings.OPERATIONS.keys():
                self.check(priv)
        return {op_key: op_result for op_key, op_result in self.cached_answers.items() if op_result}.keys()

    def clear_cache(self):
        return self.cached_answers.clear()
