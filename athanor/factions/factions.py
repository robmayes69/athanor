import re

from django.conf import settings
from django.db.models import Q

from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace
from evennia.utils.ansi import ANSIString

from athanor.core.scripts import AthanorGlobalScript
from athanor.core.objects import AthanorObject
from athanor.utils.valid import simple_name
from athanor.utils.text import partial_match

from .models import Faction
from . import messages


class AthanorFaction(AthanorObject):
    system_privileges = ('manage', 'invite', 'discipline')
    setup_ranks = {
        1: {'name': "Leader", "privileges": ('manage', 'invite', 'discipline')},
        2: {'name': 'Second', "privileges": ('manage', 'invite', 'discipline')},
        3: {'name': 'Officer', "privileges": ('invite', 'discipline')},
        4: {'name': "Member", "privileges": ()}
    }
    untouchable_ranks = (1, 2, 3)
    re_name = re.compile(r"")


    def rename(self, key):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Faction Name.")
        bridge = self.faction_bridge
        parent = bridge.db_parent
        if Faction.objects.filter(db_iname=clean_key.lower(), db_parent=parent).exclude(id=bridge).count():
            raise ValueError("Name conflicts with another Faction with the same Parent.")
        self.key = clean_key
        bridge.db_name = clean_key
        bridge.db_iname = clean_key.lower()
        bridge.db_cname = key

    def create_bridge(self, parent, key, clean_key, abbr=None, tier=0):
        if hasattr(self, 'faction_bridge'):
            return
        if parent:
            parent = parent.faction_bridge
        iabbr = abbr.lower() if abbr else None
        area, created = Faction.objects.get_or_create(db_object=self, db_parent=parent, db_name=clean_key,
                                                      db_iname=clean_key.lower(), db_cname=key, db_abbreviation=abbr,
                                                      db_iabbreviation=iabbr, db_tier=tier)
        if created:
            area.save()

    @classmethod
    def create_faction(cls, key, parent=None, abbr=None, tier=0, **kwargs):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Faction Name.")
        if Faction.objects.filter(db_iname=clean_key.lower(), db_parent=parent).count():
            raise ValueError("Name conflicts with another Faction with the same Parent.")
        obj, errors = cls.create(clean_key, **kwargs)
        if obj:
            obj.create_bridge(parent, key, clean_key, abbr, tier)
            obj.setup_faction()
        return obj, errors

    def setup_faction(self):
        privs = dict()

        def priv(priv_name):
            if priv_name in privs:
                return privs.get(priv_name)
            priv, created = self.privileges.get_or_create(db_name=priv_name)
            if created:
                priv.save()
            privs[priv_name] = priv
            return priv

        for p in self.system_privileges:
            priv(p)

        for number, details in self.setup_ranks.items():
            rank = self.create_rank(number, details["name"])
            for p in details.get('privileges', tuple()):
                rank.privileges.add(priv(p))

    def create_rank(self, number, name):
        bridge = self.faction_bridge
        exists = bridge.ranks.filter(db_rank_value=number).first()
        if exists:
            raise ValueError(f"Cannot create rank: {exists} conflicts.")
        rank, created = bridge.ranks.get_or_create(db_rank_value=number, db_name=name)
        if created:
            rank.save()
        return rank

    def effective_rank(self, character, check_admin=True):
        if check_admin and character.is_admin():
            return 0
        found = self.find_member(character)
        return found.db_rank.db_rank_number

    def find_rank(self, number):
        found = self.faction_bridge.ranks.filter(db_rank_number=number).first()
        if not found:
            raise ValueError(f"{self} does not have Rank {number}!")
        return found

    def rename_rank(self, number, new_name):
        found = self.find_rank(number)
        found.db_name = new_name

    def find_member(self, character):
        found = character.factions.filter(db_faction=self.faction_bridge)
        if not found:
            raise ValueError(f"{character} is not a member of {self}!")
        return found

    def title_member(self, character, new_title):
        found = self.find_member(character)
        found.db_title = new_title


class AthanorFactionController(AthanorGlobalScript):
    system_name = 'FACTION'
    option_dict = {
        'system_locks': ('Locks governing Faction System.', 'Lock',
                         "create:perm(Admin);delete:perm(Admin);admin:perm(Admin)"),
        'faction_locks': ('Default/Fallback locks for all Factions.', 'Lock',
                        "see:all();invite:fmember();accept:fmember();apply:all();admin:fsuperuser()")
    }

    def at_start(self):
        from django.conf import settings
        try:
            self.ndb.faction_typeclass = class_from_module(settings.BASE_FACTION_TYPECLASS,
                                                         defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.faction_typeclass = AthanorFaction

    def factions(self, parent=None):
        return AthanorFaction.objects.filter_family(faction_bridge__db_parent=parent).order_by('-faction_bridge__db_tier', 'db_key')

    def find_faction(self, search_text):
        if not search_text:
            raise ValueError("Not faction entered to search for!")
        if isinstance(search_text, AthanorFaction):
            return search_text
        if isinstance(search_text, Faction):
            return search_text.db_object
        search_tree = [text.strip() for text in search_text.split('/')] if '/' in search_text else [search_text]
        found = None
        for srch in search_tree:
            found = partial_match(srch, self.factions(found))
            if not found:
                raise ValueError(f"Faction {srch} not found!")
        return found.db_object

    def create_faction(self, session, name, description, parent=None):
        enactor = session.get_puppet_or_account()
        if not self.access(enactor, 'create', default='perm(Admin)'):
            raise ValueError("Permission denied.")
        new_faction = self.ndb.faction_typeclass.create(key=name, description=description, parent=parent)
        messages.FactionCreateMessage(source=enactor, faction=new_faction).send()
        return new_faction

    def delete_faction(self, session, faction, verify_name=None):
        enactor = session.get_puppet_or_account()
        if not self.access(enactor, 'delete', default='perm(Admin)'):
            raise ValueError("Permission denied.")
        faction = self.find_faction(faction)
        if not verify_name or not (faction.key.lower() == verify_name.lower()):
            raise ValueError("Name of the faction must match the one provided to verify deletion.")
        if faction.children.all().count():
            raise ValueError("Cannot disband a faction that has sub-factions! Either delete them or relocate them first.")
        messages.FactionDeleteMessage(source=enactor, faction=faction).send()
        faction.delete()

    def rename_faction(self, session, faction, new_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not self.access(enactor, 'admin'):
            raise ValueError("Permission denied.")
        old_path = faction.full_path()
        new_name = faction.rename(new_name)
        messages.FactionRenameMessage(source=enactor, faction=faction, old_path=old_path).send()

    def describe_faction(self, session, faction, new_description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.access(enactor, 'admin', default='fsuperuser()') or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        if not new_description:
            raise ValueError("No description entered!")
        faction.db.desc = new_description
        messages.FactionDescribeMessage(source=enactor, faction=faction).send()

    def set_tier(self, session, faction, new_tier):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if faction.parent:
            raise ValueError("Tiers are not supported for child factions!")
        if not self.access(enactor, 'admin'):
            raise ValueError("Permission denied.")
        old_tier = faction.tier
        faction.tier = new_tier
        messages.FactionTierMessage(source=enactor, faction=faction, old_tier=old_tier, new_tier=new_tier).send()

    def move_faction(self, session, faction, new_root=None):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not self.access(enactor, 'admin'):
            raise ValueError("Permission denied.")
        session.msg(new_root)
        if new_root is not None and faction == new_root:
            raise ValueError("A Faction can't own itself!")
        if new_root is None and faction.parent is None:
            raise ValueError("That doesn't make it go anywhere!")
        if new_root == faction.parent:
            raise ValueError("That doesn't make it go anywhere!")
        if new_root is not None and faction in new_root.db.ancestors:
            raise ValueError(f"Do you want {faction.full_path()} to be {new_root.full_path()}'s Grandpa and vice-versa? I don't.")
        old_path = faction.full_path()
        faction.change_parent(new_root)
        messages.FactionMoveMessage(source=enactor, faction=faction, faction_2=new_root, old_path=old_path).send()

    def set_abbreviation(self, session, faction, new_abbr):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not self.access(enactor, 'admin'):
            raise ValueError("Permission denied.")
        old_abbr = faction.abbreviation
        faction.abbreviation = new_abbr
        messages.FactionAbbreviationMessage(source=enactor, faction=faction, old_abbr=old_abbr).send()

    def set_lock(self, session, faction, new_lock):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not new_lock:
            raise ValueError("New Lock string is empty!")
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        messages.FactionLockMessage(source=enactor, faction=faction, lockstring=new_lock).send()

    def config_faction(self, session, faction, new_config):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")

    def create_privilege(self, session, faction, privilege, description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        priv = faction.create_privilege(privilege)
        priv.db.desc = description
        messages.PrivilegeCreateMessage(source=enactor, faction=faction, privilege=priv.key).send()

    def delete_privilege(self, session, faction, privilege, verify_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        priv = faction.find_privilege(privilege)
        if verify_name is None or not (priv.key.lower() == verify_name.lower()):
            raise ValueError("Privilege name and input must match!")
        messages.PrivilegeDeleteMessage(source=enactor, faction=faction, privilege=priv.key).send()
        faction.delete_privilege(priv)

    def rename_privilege(self, session, faction, privilege, new_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        priv = faction.partial_privilege(privilege)
        old_name = priv.key
        priv.rename(new_name)
        messages.PrivilegeRenameMessage(source=enactor, faction=faction, old_name=old_name, privilege=priv.key).send()

    def describe_privilege(self, session, faction, privilege, new_description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        priv = faction.partial_privilege(privilege)
        priv.db.desc = new_description
        messages.PrivilegeDescribeMessage(source=enactor, faction=faction, privilege=priv.key).send()

    def assign_privilege(self, session, faction, role, privileges):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not privileges:
            raise ValueError("No privileges entered to dole out!")
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        role = faction.partial_role(role)
        privileges = set([faction.partial_privilege(priv) for priv in privileges])
        for priv in privileges:
            role.add_privilege(priv)
        privilege_names = ', '.join([str(p) for p in privileges])
        messages.RoleAssignPrivileges(source=enactor, faction=faction, role=role.key, privileges=privilege_names).send()

    def revoke_privilege(self, session, faction, role, privileges):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not privileges:
            raise ValueError("No privileges entered to revoke!")
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        role = faction.partial_role(role)
        privileges = set([faction.partial_privilege(priv) for priv in privileges])
        for priv in privileges:
            role.remove_privilege(priv)
        privilege_names = ', '.join([str(p) for p in privileges])
        messages.RoleRevokePrivileges(source=enactor, faction=faction, role=role.key, privileges=privilege_names).send()

    def create_role(self, session, faction, role, description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        role = faction.create_role(role)
        role.db.desc = description
        messages.RoleCreateMessage(source=enactor, faction=faction, role=role.send())

    def delete_role(self, session, faction, role, verify_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        role = faction.partial_role(role)
        if verify_name is None or not role.key.lower() == verify_name.lower():
            raise ValueError("Role name and input must match!")
        messages.RoleDeleteMessage(source=enactor, faction=faction, role=role.key).send()
        faction.delete_role(role)

    def rename_role(self, session, faction, role, new_name):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        role = faction.partial_role(role)
        old_name = role.key
        role.rename(new_name)
        messages.RoleRenameMessage(source=enactor, faction=faction, role=role.key, old_name=old_name).send()

    def describe_role(self, session, faction, role, new_description):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        if not (faction.is_supermember(enactor) or self.access(enactor, 'admin')):
            raise ValueError("Permission denied.")
        role = faction.partial_role(role)
        role.db.desc = new_description
        messages.RoleDescribeMessage(source=enactor, faction=faction, role=role.key).send()

    def direct_add_member(self, session, faction, character):
        link = self.add_member(session, faction, character.entity)

    def kick_member(self, session, faction, character):
        self.remove_member(session, faction, character.entity)

    def leave_faction(self, session, faction, confirm):
        pass

    def add_member(self, session, faction, entity):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(entity)
        if link.member:
            raise ValueError(f"{entity} is already a member of {faction}!")
        link.member = True
        return link

    def remove_member(self, session, faction, entity):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(entity, create=False)
        link.member = False
        link.is_supermember = False
        link.roles.all().delete()
        del link.db.title
        if not link.db.reputation:
            link.delete()

    def send_application(self, session, faction, character, pitch):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(character)
        if link.is_applying:
            raise ValueError("You already applied!")
        if not pitch:
            raise ValueError("Must include a pitch!")
        link.is_applying = True
        link.db.application_pitch = pitch

    def withdraw_application(self, session, faction, character):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(character, create=False)
        if not link.is_applying:
            raise ValueError("You already applied!")
        link.is_applying = False
        del link.db.application_pitch
        if not link.db.reputation:
            link.delete()

    def accept_application(self, session, faction, character):
        pass

    def invite_character(self, session, faction, character):
        pass

    def uninvite_character(self, session, faction, character):
        pass

    def accept_invite(self, session, link):
        pass

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

    def title_member(self, session, faction, character, new_title):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(character.entity)
        link.db.title = new_title

    def set_supermember(self, session, faction, character, new_status):
        enactor = session.get_puppet_or_account()
        faction = self.find_faction(faction)
        link = faction.link(character.entity)
        link.is_supermember = new_status
