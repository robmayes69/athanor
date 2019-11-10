from evennia.typeclasses.models import TypeclassBase
from features.factions.models import FactionDB, FactionMembershipDB, FactionRoleDB, FactionPrivilegeDB
from utils.valid import simple_name


class DefaultFaction(FactionDB, metaclass=TypeclassBase):

    def at_first_save(self, *args, **kwargs):
        pass

    @property
    def ancestors(self):
        full_list = list()
        p = self.parent
        while p is not None:
            full_list.append(p)
            p = p.parent
        full_list.reverse()
        return full_list

    @classmethod
    def validate_key(cls, key_text, rename_from=None, parent=None):
        if not key_text:
            raise ValueError("Factions must have a name!")
        key_text = simple_name(key_text, option_key='Faction Name')
        query = FactionDB.objects.filter_family(db_key__ixact=key_text, db_parent=parent)
        if rename_from:
            query = query.exclude(id=rename_from)
        if query.count():
            raise ValueError("Another Faction already uses that name!")
        return key_text

    @classmethod
    def create(cls, *args, **kwargs):
        parent = kwargs.get('parent', None)
        if parent and not isinstance(parent, FactionDB):
            raise ValueError("Parent must be an instance of a Faction!")

        key = kwargs.get('key', None)
        key = cls.validate_key(key, parent=parent)
        tier = kwargs.get('tier', 0)

        new_faction = cls(db_key=key, db_tier=tier, db_parent=parent)
        new_faction.save()
        return new_faction

    def entity_has_privilege(self, entity, privilege_name, admin_bypass=True):
        if admin_bypass and entity.is_admin:
            return True
        found_privilege = self.privileges.filter(key__iexact=privilege_name).first()
        if not found_privilege:
            return False
        if found_privilege.non_members:
            return True
        membership = self.memberships.filter(db_entity=entity).first()
        if not membership:
            return False
        if found_privilege.all_members:
            return True
        return found_privilege in membership.privileges

    def create_new_membership(self, entity):
        pass

    def delete_membership(self, entity):
        pass

    def create_privilege(self, privilege_name):
        if self.privileges.filter(key__iexact=privilege_name).count():
            pass
        new_privilege, created = self.privileges.get_or_create(key=privilege_name)
        if created:
            new_privilege.save()
        return new_privilege

    def delete_privilege(self, privilege_name):
        found_privilege = self.privileges.filter(key__iexact=privilege_name).first()
        if not found_privilege:
            pass
        found_privilege.delete()

    def create_role(self, role_name):
        if self.roles.filter(key__iexact=role_name).count():
            pass
        new_role, created = self.roles.get_or_create(key=role_name)
        if created:
            new_role.save()
        return new_role

    def delete_role(self, role_name):
        found_role = self.roles.filter(key__iexact=role_name).first()
        if not found_role:
            pass
        found_role.delete()

    def grant_privilege_to_member(self, privilege, member):
        pass

    def revoke_privilege_from_member(self, privilege, member):
        pass

    def grant_privilege_to_role(self, privilege, role):
        pass

    def revoke_privilege_from_role(self, privilege, role):
        pass

    def grant_role_to_member(self, role, member):
        pass

    def revoke_role_from_remember(self, role, member):
        pass


class DefaultFactionMembership(FactionMembershipDB, metaclass=TypeclassBase):

    @classmethod
    def create(cls, *args, **kwargs):
        pass

    def add_role(self, role):
        pass

    def remove_role(self, role):
        pass

    def add_privilege(self, privilege):
        pass

    def remove_privilege(self, privilege):
        pass


class DefaultFactionRole(FactionRoleDB, metaclass=TypeclassBase):
    pass


class DefaultFactionPrivilege(FactionPrivilegeDB, metaclass=TypeclassBase):
    pass
