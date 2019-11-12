from django.db import models
from evennia.typeclasses.models import TypedObject


class AllianceDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultAlliance"
    __defaultclasspath__ = "features.factions.factions.DefaultAlliance"
    __applabel__ = "factions"

    db_tier = models.PositiveIntegerField(default=0, null=False, blank=False)
    db_abbreviation = models.CharField(max_length=20, null=True, blank=True, unique=True)
    db_global_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)


class AllianceLinkDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultAllianceLink"
    __defaultclasspath__ = "features.factions.factions.DefaultAllianceLink"
    __applabel__ = "factions"

    db_alliance = models.ForeignKey(AllianceDB, null=False, on_delete=models.CASCADE, related_name='relationships')
    db_entity = models.ForeignKey('core.EntityMapDB', on_delete=models.CASCADE, related_name='alliance_links')

    class Meta:
        verbose_name = 'AllianceLink'
        verbose_name_plural = 'AllianceLinks'
        unique_together = (('db_alliance', 'db_entity'),)


class FactionDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultFaction"
    __defaultclasspath__ = "features.factions.factions.DefaultFaction"
    __applabel__ = "factions"

    db_alliance = models.ForeignKey(AllianceDB, null=True, on_delete=models.SET_NULL, related_name='factions')
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


class FactionLinkDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultFactionLink"
    __defaultclasspath__ = "features.factions.factions.DefaultFactionLink"
    __applabel__ = "factions"

    db_faction = models.ForeignKey(FactionDB, null=False, on_delete=models.CASCADE, related_name='memberships')
    db_entity = models.ForeignKey('core.EntityMapDB', null=False, on_delete=models.CASCADE, related_name='faction_links')
    db_membership = models.BooleanField(default=False)
    db_primary_role = models.ForeignKey(FactionRoleDB, related_name='primaries', null=True, on_delete=models.CASCADE)
    db_roles = models.ManyToManyField(FactionRoleDB, related_name='links')

    class Meta:
        verbose_name = 'FactionLink'
        verbose_name_plural = 'FactionLinks'
        unique_together = (('db_faction', 'db_entity'),)


class DivisionDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultDivision"
    __defaultclasspath__ = "features.factions.factions.DefaultDivision"
    __applabel__ = "factions"

    db_faction = models.ForeignKey(FactionDB, on_delete=models.PROTECT, related_name='divisons')
    db_description = models.TextField(blank=True, null=True)
    db_administrators = models.ManyToManyField('objects.ObjectDB', related_name='division_admin')
    db_tier = models.PositiveIntegerField(default=0, null=False, blank=False)
    db_abbreviation = models.CharField(max_length=20, null=True, blank=True, unique=True)
    db_global_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)
    db_membership_typeclass = models.CharField(max_length=255, null=True)
    db_privilege_typeclass = models.CharField(max_length=255, null=True)
    db_role_typeclass = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = (('db_faction', 'db_key'),)



