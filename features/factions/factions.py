import re
from django.conf import settings
from django.db.models import Q
from evennia.typeclasses.models import TypeclassBase
from features.factions.models import FactionDB, FactionLinkDB, FactionRoleDB, FactionPrivilegeDB, FactionRoleLinkDB
from features.core.base import AthanorTypeEntity
from evennia.typeclasses.managers import TypeclassManager
from typeclasses.scripts import GlobalScript
from utils.valid import simple_name
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from utils.text import partial_match
from features.core.base import AthanorTreeEntity

_PERM_RE = re.compile(r"^[a-zA-Z_0-9]+$")


class DefaultFaction(FactionDB, AthanorTypeEntity, AthanorTreeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        FactionDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)

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

    def find_privilege(self, privilege_name):
        if isinstance(privilege_name, DefaultFactionPrivilege) and privilege_name.faction == self:
            return privilege_name
        found = self.privileges.filter(db_key__iexact=privilege_name).first()
        if found:
            return found
        raise ValueError("Privilege not found!")

    def partial_privilege(self, privilege_name):
        choices = self.privileges.all()
        if not choices:
            raise ValueError("No Privileges to choose from!")
        found = partial_match(privilege_name, choices)
        if found:
            return found
        raise ValueError("Privilege not found!")

    def create_privilege(self, privilege_name):
        privilege_typeclass = self.get_privilege_typeclass()
        return privilege_typeclass.create(faction=self, key=privilege_name)

    def delete_privilege(self, privilege_name):
        found_privilege = self.find_privilege(privilege_name)
        found_privilege.delete()

    def find_role(self, role_name):
        if isinstance(role_name, DefaultFactionRole) and role_name.faction == self:
            return role_name
        found = self.roles.filter(db_key__iexact=role_name).first()
        if found:
            return found
        raise ValueError("Role not found!")

    def partial_role(self, role_name):
        choices = self.roles.all()
        if not choices:
            raise ValueError("No Roles to choose from!")
        found = partial_match(role_name, choices)
        if found:
            return found
        raise ValueError("Role not found!")

    def create_role(self, role_name):
        role_typeclass = self.get_role_typeclass()
        return role_typeclass.create(faction=self, key=role_name)

    def delete_role(self, role_name):
        found_role = self.find_role(role_name)
        found_role.delete()

    def assign_role(self, role_name, entity):
        found_role = self.find_role(role_name)

    def revoke_role(self, role_name, entity):
        found_role = self.find_role(role_name)

    def get_child_typeclass(self):
        return self.get_typeclass_field('child_typeclass', settings.BASE_FACTION_TYPECLASS)

    def get_link_typeclass(self):
        return self.get_typeclass_field('link_typeclass', settings.BASE_FACTION_LINK_TYPECLASS)

    def get_privilege_typeclass(self):
        return self.get_typeclass_field('privilege_typeclass', settings.BASE_FACTION_PRIVILEGE_TYPECLASS)

    def get_role_typeclass(self):
        return self.get_typeclass_field('role_typeclass', settings.BASE_FACTION_ROLE_TYPECLASS)

    def get_role_link_typeclass(self):
        return self.get_typeclass_field('role_link_typeclass', settings.BASE_FACTION_ROLE_LINK_TYPECLASS)

    def members(self):
        return self.memberships.filter(db_member=True)

    def is_member(self, entity):
        all_factions = list()
        all_factions.append(self)
        all_factions += self.descendants
        if entity.faction_links.filter(db_faction__in=all_factions).filter(Q(db_member=True) | Q(db_is_superuser=True)).count():
            return True


class DefaultFactionLink(FactionLinkDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        FactionLinkDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)

    @classmethod
    def create(cls, *args, **kwargs):
        pass

    def add_role(self, role):
        pass

    def remove_role(self, role):
        pass


class DefaultFactionRole(FactionRoleDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        FactionRoleDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)

    def add_privilege(self, privilege):
        pass

    def remove_privilege(self, privilege):
        pass


class DefaultFactionPrivilege(FactionPrivilegeDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        FactionPrivilegeDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultFactionRoleLink(FactionRoleLinkDB, AthanorTypeEntity, metaclass=TypeclassBase):
    objects = TypeclassManager()

    def __init__(self, *args, **kwargs):
        FactionRoleLinkDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultFactionController(GlobalScript):
    system_name = 'FACTION'
    option_dict = {
    }

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.faction_typeclass = class_from_module(settings.BASE_FACTION_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.theme_typeclass = DefaultFaction

    def factions(self, parent=None):
        return DefaultFaction.objects.filter_family(db_parent=parent).order_by('-db_tier', 'db_key')

    def find_faction(self, search_text):
        if isinstance(search_text, DefaultFaction):
            return search_text
        search_tree = [text.strip() for text in search_text.split('/')] if '/' in search_text else [search_text]
        found = None
        for srch in search_tree:
            found = partial_match(srch, self.factions(found))
            if not found:
                raise ValueError(f"Faction {srch} not found!")
        return found

    def create_faction(self, session, name, description, parent=None):
        enactor = session.get_puppet_or_account()
        new_faction = self.ndb.faction_typeclass.create(key=name, description=description, parent=parent)
        return new_faction

    def delete_faction(self, session, faction, verify_name=None):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not faction.key.lower() == verify_name.lower():
            raise ValueError("Name of the faction must match the one provided to verify deletion.")
        if faction.children.all().count():
            raise ValueError("Cannot disband a faction that has sub-factions! Either delete them or relocate them first.")
        faction.delete()

    def rename_faction(self, session, faction, new_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        faction.rename(new_name)

    def describe_faction(self, session, faction, new_description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not new_description:
            raise ValueError("No description entered!")
        faction.db.desc = new_description

    def set_tier(self, session, faction, new_tier):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        faction.tier = new_tier

    def move_faction(self, session, faction, new_root=None):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        faction.change_parent(new_root)

    def set_abbreviation(self, session, faction, new_abbr):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        faction.abbreviation = new_abbr

    def set_lock(self, session, faction, new_lock):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not new_lock:
            raise ValueError("New Lock string is empty!")

    def config_faction(self, session, faction, new_config):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)

    def create_privilege(self, session, faction, privilege, description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)

        priv = faction.create_privilege(privilege)
        priv.db.desc = description

    def delete_privilege(self, session, faction, privilege, verify_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        priv = faction.find_privilege(privilege)
        if not priv.key.lower() == verify_name.lower():
            raise ValueError("Privilege name and input must match!")
        faction.delete_privilege(priv)

    def rename_privilege(self, session, faction, privilege, new_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        priv = faction.find_privilege(privilege)
        old_name = priv.key
        priv.rename(new_name)

    def describe_privilege(self, session, faction, privilege, new_description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        priv = faction.find_privilege(privilege)
        priv.db.desc = new_description

    def assign_privilege(self, session, faction, role, privileges):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        role = faction.find_role(role)
        privileges = [faction.find_privilege(priv) for priv in privileges]
        for priv in privileges:
            role.add_privilege(priv)

    def revoke_privilege(self, session, faction, role, privilege):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        role = faction.find_role(role)
        privileges = [faction.find_privilege(priv) for priv in privileges]
        for priv in privileges:
            role.remove_privilege(priv)

    def create_role(self, session, faction, role, description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        role = faction.create_role(role)
        role.db.desc = description

    def delete_role(self, session, faction, role, verify_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        role = faction.find_role(role)
        if not role.key.lower() == verify_name.lower():
            raise ValueError("Role name and input must match!")
        faction.delete_role(role)

    def rename_role(self, session, faction, role, new_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        role = faction.find_role(role)
        old_name = role.key
        role.rename(new_name)

    def describe_role(self, session, faction, role, new_description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        role = faction.find_role(role)
        role.db.desc = new_description

    def add_member(self, session, faction, entity):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(entity)
        link.member = True

    def remove_member(self, session, faction, entity):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(entity)
        link.member = False
        link.roles.all().delete()
        del link.db.title
        if not link.db.reputation:
            link.delete()

    def assign_role(self, session, faction, entity, role):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(entity)
        role = faction.find_role(role)
        link.add_role(role)

    def revoke_role(self, session, faction, entity, role):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(entity)
        role = faction.find_role(role)
        link.remove_role(role)

    def title_member(self, session, faction, entity, new_title):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(entity)
        link.db.title = new_title

    def set_superuser(self, session, faction, entity, new_status):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(entity)
        link.is_superuser = new_status
