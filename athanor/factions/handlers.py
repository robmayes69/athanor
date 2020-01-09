class FactionHandler(object):

    def __init__(self, owner):
        self.owner = owner

    def is_member(self, faction, check_admin=True):

        def recursive_check(fact):
            checking = fact
            while checking:
                if checking == faction:
                    return True
                checking = checking.db_parent
            return False

        if hasattr(faction, 'faction_bridge'):
            faction = faction.faction_bridge
        if check_admin and self.owner.is_admin():
            return True
        if self.factions.filter(db_faction=faction).count():
            return True
        all_factions = self.factions.all()
        for fac in all_factions:
            if recursive_check(fac.db_faction):
                return True
        return False

class AllianceHandler(object):

    def __init__(self, owner):
        self.owner = owner


class DivisionHandler(object):

    def __init__(self, owner):
        self.owner = owner
