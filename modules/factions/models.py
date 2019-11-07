from django.db import models
from evennia.typeclasses.models import TypedObject
from evennia.typeclasses.managers import TypeclassManager


class FactionDB(TypedObject):
    __settingclasspath__ = "modules.factions.factions.DefaultFaction"
    __defaultclasspath__ = "modules.factions.factions.DefaultFaction"
    __applabel__ = "factions"

    db_parent = models.ForeignKey('self', null=True, on_delete=models.DO_NOTHING, related_name='children')
    db_administrators = models.ManyToManyField('objects.ObjectDB', related_name='faction_admin')
    db_tier = models.PositiveIntegerField(default=0, null=False, blank=False)

    class Meta:
        verbose_name = 'Faction'
        verbose_name_plural = 'Factions'
        unique_together = (('db_key', 'db_parent'),)

    objects = TypeclassManager()


class FactionPrivilege(models.Model):
    faction = models.ForeignKey(FactionDB, null=False, on_delete=models.CASCADE, related_name='privileges')
    key = models.CharField(blank=False, null=False, max_length=255)
    child_inherits = models.BooleanField(default=False, null=False)
    ancestor_inherits = models.BooleanField(default=False, null=False)
    all_members = models.BooleanField(default=False, null=False)
    non_members = models.BooleanField(default=False, null=False)
    specific_members = models.ManyToManyField('objects.ObjectDB', related_name='faction_privileges')
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('faction', 'key'),)

    def __str__(self):
        return self.key


class FactionRole(models.Model):
    faction = models.ForeignKey(FactionDB, null=False, on_delete=models.CASCADE, related_name='roles')
    key = models.CharField(blank=False, null=False, max_length=255)
    description = models.TextField(null=True, blank=True)
    privileges = models.ManyToManyField(FactionPrivilege, related_name='roles')
    sort_order = models.PositiveIntegerField(default=0, blank=False, null=False)
    can_bestow = models.ManyToManyField('self', related_name='grantable_by')

    class Meta:
        unique_together = (('faction', 'key'),)

    def __str__(self):
        return self.key


class FactionMembershipDB(TypedObject):
    __settingclasspath__ = "modules.factions.factions.DefaultFactionMembership"
    __defaultclasspath__ = "modules.factions.factions.DefaultFactionMembership"
    __applabel__ = "faction_memberships"

    db_faction = models.ForeignKey(FactionDB, null=False, on_delete=models.CASCADE, related_name='memberships')
    db_entity = models.ForeignKey('objects.ObjectDB', null=False, on_delete=models.CASCADE, related_name='faction_memberships')

    db_roles = models.ManyToManyField(FactionRole, related_name='memberships')
    db_privileges = models.ManyToManyField(FactionPrivilege, related_name='memberships')

    class Meta:
        verbose_name = 'Faction Membership'
        verbose_name_plural = 'Faction Memberships'
        unique_together = (('db_entity', 'db_faction'),)

    objects = TypeclassManager()
