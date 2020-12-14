import re
from dataclasses import dataclass
from typing import Dict, List
from athanor.identities.models import IdentityDB

RE_ACL = re.compile(r"^(?P<addremove>\+|-)(?P<deny>!)?(?P<prefix>\w+):(?P<name>.*?)(?::(?P<mode>.*?))(?P<perms>(\/\w+){1,})$")
# +!A:Volund:friends/read/boogaloo


@dataclass
class ACLEntry:
    remove: bool
    deny: bool
    identity: IdentityDB
    mode: str
    perms: List[str]


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

    def parse_acl(self, entry, enactor=None) -> List[ACLEntry]:
        entries = list()

        for s in entry.split(','):
            if not (match := RE_ACL.match(s)):
                raise ValueError(f"invalid ACL entry: {s}")
            gd = match.groupdict()
            deny = bool(gd.get('deny', False))
            remove = True if gd.get('addremove') == '-' else False
            if enactor:
                identity = enactor.find_identity(prefix=gd.get('prefix'), name=gd.get('name'))
            else:
                identity = IdentityDB.objects.filter(db_namespace__db_prefix__iexact=gd.get('prefix'), db_key__iexact=gd.get('name')).first()
            if not identity:
                raise ValueError(f"Identity Not found: {s}")
            mode = gd.get('mode', '')
            perms = [p.strip().lower() for p in gd.get('perms').split('/') if p]
            p_dict = self.perm_dict()
            for perm in perms:
                if perm not in p_dict:
                    raise ValueError(f"Permission not found: {perm}")

            acl_e = ACLEntry(remove, deny, identity, mode, perms)
            entries.append(acl_e)

        return entries

    def apply_acl(self, entries: List[ACLEntry], report_to=None):
        p_dict = self.perm_dict()
        for entry in entries:
            if not (row := self.acl_entries.filter(identity=entry.identity, mode=entry.mode).first()):
                row = self.acl_entries.create(identity=entry.identity, mode=entry.mode)
            bitfield = int(row.allow_permissions if not entry.deny else row.deny_permissions)
            if entry.remove:
                for perm in entry.perms:
                    pval = p_dict.get(perm)
                    if pval & bitfield:
                        bitfield -= pval
            else:
                for perm in entry.perms:
                    pval = p_dict.get(perm)
                    bitfield = bitfield | pval
            if entry.deny:
                row.deny_permissions = bitfield
            else:
                row.allow_permissions = bitfield
            row.save()
            if row.allow_permissions == 0 and row.deny_permissions == 0:
                row.delete()
