from django.db import models
from evennia.typeclasses.models import TypedObject


class FactionDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultFaction"
    __defaultclasspath__ = "features.factions.factions.DefaultFaction"
    __applabel__ = "factions"

    db_parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT, related_name='children')
    db_administrators = models.ManyToManyField('objects.ObjectDB', related_name='faction_admin')
    db_tier = models.PositiveIntegerField(default=0, null=False, blank=False)
    db_abbreviation = models.CharField(max_length=20, null=True, blank=True, unique=True)
    db_global_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)
    db_membership_typeclass = models.CharField(max_length=255, null=True)
    db_privilege_typeclass = models.CharField(max_length=255, null=True)
    db_role_typeclass = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = 'Faction'
        verbose_name_plural = 'Factions'
        unique_together = (('db_key', 'db_parent'),)


class FactionPrivilegeDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultFactionPrivilege"
    __defaultclasspath__ = "features.factions.factions.DefaultFactionPrivilege"
    __applabel__ = "factions"

    db_faction = models.ForeignKey(FactionDB, null=False, on_delete=models.CASCADE, related_name='privileges')
    db_description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('db_faction', 'db_key'),)
        verbose_name = 'FactionPrivilege'
        verbose_name_plural = 'FactionPrivileges'

    def __str__(self):
        return self.key


class FactionRoleDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultFactionRole"
    __defaultclasspath__ = "features.factions.factions.DefaultFactionRole"
    __applabel__ = "factions"

    db_faction = models.ForeignKey(FactionDB, null=False, on_delete=models.CASCADE, related_name='roles')
    db_description = models.TextField(null=True, blank=True)
    db_privileges = models.ManyToManyField(FactionPrivilegeDB, related_name='roles')
    db_rank = models.PositiveIntegerField(default=0, null=False, blank=False)

    class Meta:
        unique_together = (('db_faction', 'db_key'),)
        verbose_name = 'FactionRole'
        verbose_name_plural = 'FactionRoles'

    def __str__(self):
        return self.key


class FactionMembershipDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultFactionMembership"
    __defaultclasspath__ = "features.factions.factions.DefaultFactionMembership"
    __applabel__ = "faction_memberships"

    db_faction = models.ForeignKey(FactionDB, null=False, on_delete=models.CASCADE, related_name='memberships')
    db_entity = models.ForeignKey('objects.ObjectDB', null=False, on_delete=models.CASCADE, related_name='faction_memberships')

    db_roles = models.ManyToManyField(FactionRoleDB, related_name='memberships')

    class Meta:
        verbose_name = 'Faction Membership'
        verbose_name_plural = 'Faction Memberships'
        unique_together = (('db_entity', 'db_faction'),)

