import re

from evennia.utils.ansi import ANSIString

from athanor.gamedb.objects import AthanorObject
from athanor.gamedb.models import FactionBridge


class AthanorAlliance(AthanorObject):
    pass


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
    lockstring = ""

    def rename(self, key):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Faction Name.")
        bridge = self.faction_bridge
        parent = bridge.db_parent
        if FactionBridge.objects.filter(db_iname=clean_key.lower(), db_parent=parent).exclude(id=bridge).count():
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
        area, created = FactionBridge.objects.get_or_create(db_object=self, db_parent=parent, db_name=clean_key,
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
        if FactionBridge.objects.filter(db_iname=clean_key.lower(), db_parent=parent).count():
            raise ValueError("Name conflicts with another Faction with the same Parent.")
        obj, errors = cls.create(clean_key, **kwargs)
        if obj:
            obj.create_bridge(parent, key, clean_key, abbr, tier)
            obj.setup_faction()
        else:
            raise ValueError(errors)
        return obj

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
        if (exists := bridge.ranks.filter(db_rank_value=number).first()):
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
        if not (found := character.factions.filter(db_faction=self.faction_bridge)):
            raise ValueError(f"{character} is not a member of {self}!")
        return found

    def title_member(self, character, new_title):
        found = self.find_member(character)
        found.db_title = new_title


class AthanorDivision(AthanorObject):
    pass
