from django.db import models
from evennia.typeclasses.models import TypedObject


class FactionDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultFaction"
    __defaultclasspath__ = "features.factions.factions.DefaultFaction"
    __applabel__ = "factions"

    db_parent = models.ForeignKey('self', null=True, related_name='children', on_delete=models.PROTECT)
    db_tier = models.PositiveIntegerField(default=0, null=False, blank=False)
    db_abbreviation = models.CharField(max_length=20, null=True, blank=True, unique=True)
    db_global_identifier = models.CharField(max_length=255, null=True, blank=False, unique=True)
    db_child_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+', on_delete=models.PROTECT)
    db_link_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+', on_delete=models.PROTECT)
    db_privilege_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+', on_delete=models.PROTECT)
    db_role_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+', on_delete=models.PROTECT)
    db_role_link_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='+', on_delete=models.PROTECT)

    class Meta:
        unique_together = (('db_parent', 'db_key'),)
        verbose_name = 'Faction'
        verbose_name_plural = 'Factions'


class FactionPrivilegeDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultFactionPrivilege"
    __defaultclasspath__ = "features.factions.factions.DefaultFactionPrivilege"
    __applabel__ = "factions"

    db_faction = models.ForeignKey(FactionDB, null=False, on_delete=models.CASCADE, related_name='privileges')

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
    db_member = models.PositiveSmallIntegerField(default=0)  # set this 1 for member, 2 for superuser of Faction.
    db_sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'FactionLink'
        verbose_name_plural = 'FactionLinks'
        unique_together = (('db_faction', 'db_entity'),)
        index_together = (('db_faction', 'db_member', 'db_sort_order'),)


class FactionRoleLinkDB(TypedObject):
    __settingclasspath__ = "features.factions.factions.DefaultFactionRoleLink"
    __defaultclasspath__ = "features.factions.factions.DefaultFactionRoleLink"
    __applabel__ = "factions"

    db_link = models.ForeignKey(FactionLinkDB, null=False, on_delete=models.CASCADE, related_name='role_links')
    db_role = models.ForeignKey(FactionRoleDB, null=False, on_delete=models.CASCADE, related_name='role_links')
    db_grantable = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'FactionLink'
        verbose_name_plural = 'FactionLinks'
        unique_together = (('db_link', 'db_role', 'db_grantable'),)
