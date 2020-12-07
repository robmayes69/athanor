from typing import Dict


class ACLMixin:
    """
    This class must be added to a Model as a Mixin. No other class.
    """
    permissions_base = {"full": 1}
    permissions_custom = {}

    def perm_dict(self) -> Dict[str, int]:
        d = dict()
        d.update(self.permissions_base)
        d.update(self.permissions_custom)
        return d

    def is_owner(self, obj_to_check) -> bool:
        return False

    def check_access(self, accessor, perm: str, mode: str = "") -> bool:
        return self.check_acl(accessor, perm, mode)

    def check_acl(self, accessor, perm: str, mode: str = "") -> bool:
        bit = self.perm_dict()[perm]
        entries = list()

        for entry in self.acl_entries.filter(mode=mode).order_by("identity__db_namespace__db_priority", "identity__db_key"):
            if entry.identity.represents(accessor, mode):
                # First, check for Denies.
                if entry.deny_permissions & 1 or entry.deny_permissions & bit:
                    return False
                entries.append(entry)

        for entry in entries:
            # Then check for Allows.
            if entry.allow_permissions & 1 or entry.allow_permissions & bit:
                return True

        return False
