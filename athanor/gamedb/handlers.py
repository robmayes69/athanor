from django.conf import settings

import athanor


class OperationHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.cached_answers = dict()

    def check(self, operation):
        if (found := self.cached_answers.get(operation, None)) is not None:
            return found
        op_data = settings.OPERATIONS.get(operation, dict())
        if not op_data:
            return False
        op_perm = op_data.get("permission", "Developer")
        if self.owner.check_lock(f'pperm({op_perm})'):
            self.cached_answers[operation] = True
            return True
        all_roles = self.owner.roles.all()
        for role_key, role_def in athanor.CONTROLLER_MANAGER.get('account').roles.items():
            if role_key not in all_roles:
                continue
            if operation in role_def.get('operations', set()):
                self.cached_answers[operation] = True
                return True
        self.cached_answers[operation] = False
        return False

    def all(self):
        if len(self.cached_answers.keys()) != len(settings.OPERATIONS):
            for priv in settings.OPERATIONS.keys():
                self.check(priv)
        return {op_key: op_result for op_key, op_result in self.cached_answers.items() if op_result}.keys()

    def clear_cache(self):
        return self.cached_answers.clear()
