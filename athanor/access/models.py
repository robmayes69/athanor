"""
I COULD use GenericForeignKey for ACL, but I think it'd be better to instead create many
tables for much better indexing effiand full exploitation of Foreign Key cascading.
"""
from django.db import models
from typing import Dict


class AbstractACLEntry(models.Model):
    # This Generic Foreign Key is the object being 'accessed'.
    #resource = models.ForeignKey('something', related_name='acl_entries', on_delete=models.CASCADE)

    identity = models.ForeignKey('identities.IdentityDB', related_name='+', on_delete=models.CASCADE)
    mode = models.CharField(max_length=30, null=False, blank=True, default='')
    allow_permissions = models.PositiveIntegerField(default=0, null=False)
    deny_permissions = models.PositiveIntegerField(default=0, null=False)

    class Meta:
        #unique_together = (('resource', 'identity', 'mode'),)
        abstract = True

    def base_string(self):
        base = f"{self.identity.db_namespace.db_prefix}:{self.identity.db_key}"
        if self.mode:
            base += f':{self.mode}'
        return base

    def perm_string(self, bitfield: int, p_dict: Dict[str, int] = None):
        if p_dict is None:
            p_dict = self.resource.acl.perm_dict()
        return '/'.join([k for k, v in p_dict.items() if v & bitfield])

    def render(self, deny: bool=False, p_dict: Dict[str, int] = None):
        if p_dict is None:
            p_dict = self.resource.acl.perm_dict()
        if deny:
            return f"!{self.base_string()}/{self.perm_string(int(self.deny_permissions), p_dict)}"
        else:
            return f"{self.base_string()}/{self.perm_string(int(self.allow_permissions), p_dict)}"

    def __repr__(self):
        p_dict = self.resource.acl.perm_dict()
        return f"<{self.__class__.__name__}: {self.render(False, p_dict)} - {self.render(True, p_dict)}>"


class ObjectACL(AbstractACLEntry):
    resource = models.ForeignKey('objects.ObjectDB', related_name='acl_entries', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('resource', 'identity', 'mode'),)


class AccountACL(AbstractACLEntry):
    resource = models.ForeignKey('accounts.AccountDB', related_name='acl_entries', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('resource', 'identity', 'mode'),)


class ScriptACL(AbstractACLEntry):
    resource = models.ForeignKey('scripts.ScriptDB', related_name='acl_entries', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('resource', 'identity', 'mode'),)


class ChannelACL(AbstractACLEntry):
    resource = models.ForeignKey('comms.ChannelDB', related_name='acl_entries', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('resource', 'identity', 'mode'),)


class IdentityACL(AbstractACLEntry):
    resource = models.ForeignKey('identities.IdentityDB', related_name='acl_entries', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('resource', 'identity', 'mode'),)


class ZoneACL(AbstractACLEntry):
    resource = models.ForeignKey('zones.ZoneDB', related_name='acl_entries', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('resource', 'identity', 'mode'),)


class SectorACL(AbstractACLEntry):
    resource = models.ForeignKey('sectors.SectorDB', related_name='acl_entries', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('resource', 'identity', 'mode'),)
