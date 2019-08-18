from django.db import models
from django.conf import settings
from evennia.typeclasses.models import TypeclassBase
from modules.factions.models import FactionDB, FactionMembershipDB
from future.utils import with_metaclass


class DefaultFaction(with_metaclass(TypeclassBase, FactionDB)):

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


class DefaultFactionMembership(with_metaclass(TypeclassBase, FactionMembershipDB)):

    def add_role(self, role):
        pass

    def remove_role(self, role):
        pass

    def add_privilege(self, privilege):
        pass

    def remove_privilege(self, privilege):
        pass