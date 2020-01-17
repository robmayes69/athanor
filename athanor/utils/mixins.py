from django.conf import settings

from evennia.locks.lockhandler import LockHandler
from evennia.utils.utils import lazy_property


_PERMISSION_HIERARCHY = [p.lower() for p in settings.PERMISSION_HIERARCHY]




class HasLocks(object):
    lockstring = ""

    @lazy_property
    def locks(self):
        return LockHandler(self)

    @property
    def lock_storage(self):
        return self.db_lock_storage

    @lock_storage.setter
    def lock_storage(self, value):
        self.db_lock_storage = value

    def access(self, accessing_obj, access_type="read", default=False, no_superuser_bypass=False, **kwargs):
        return self.locks.check(
            accessing_obj,
            access_type=access_type,
            default=default,
            no_superuser_bypass=no_superuser_bypass,
        )

    def check_permstring(self, permstring):
        if hasattr(self, "account"):
            if (
                    self.account
                    and self.account.is_superuser
                    and not self.account.attributes.get("_quell")
            ):
                return True
        else:
            if self.is_superuser and not self.attributes.get("_quell"):
                return True

        if not permstring:
            return False
        perm = permstring.lower()
        perms = [p.lower() for p in self.permissions.all()]
        if perm in perms:
            # simplest case - we have a direct match
            return True
        if perm in _PERMISSION_HIERARCHY:
            # check if we have a higher hierarchy position
            ppos = _PERMISSION_HIERARCHY.index(perm)
            return any(
                True
                for hpos, hperm in enumerate(_PERMISSION_HIERARCHY)
                if hperm in perms and hpos > ppos
            )
        # we ignore pluralization (english only)
        if perm.endswith("s"):
            return self.check_permstring(perm[:-1])

        return False
