from evennia.locks.lockhandler import LockHandler
from evennia.utils.utils import lazy_property
from athanor.items.handlers import InventoryHandler


class HasInventory(InventoryHandler):
    default_inventory = "general"

    @lazy_property
    def items(self):
        return InventoryHandler(self)


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
