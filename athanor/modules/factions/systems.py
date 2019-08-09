from athanor import AthException
from athanor.base.systems import AthanorSystem
from athanor.utils.text import partial_match, sanitize_string
from athanor.modules.factions.scripts import FactionScript


class FactionSystem(AthanorSystem):
    key = 'faction'
    system_name = 'FACTION'
    load_order = -48
    settings_data = (
        ('faction_locks', 'Default locks for new Factions?', 'lock', ''),
        ('private_start', 'Should new Factions be private to start with?', 'bool', True),
    )

    def base_factions(self):
        return sorted([f for f in FactionScript.objects.filter_family() if f.parent is None],
                      key=lambda g: g.key)

    def base_visible(self, session):
        return [f for f in self.base_factions() if (f.locks.check(session.account, 'see') or not f.db.private)]

    def create_faction(self, session, name=None, parent=None, private=None):
        if private is None:
            private = self['private_start']
        if parent:
            parent = self.find_faction(session, parent)

    def find_faction(self, session, search_text):
        if not search_text:
            raise AthException("No search text!")
        if isinstance(search_text, FactionScript):
            return search_text
        next_search = None
        if '/' in sanitize_string(search_text):
            search_text, next_search = search_text.split('/', 1)
            next_search = sanitize_string(next_search)
        found = partial_match(search_text, self.children)
        if found and next_search:
            return found.find_child(next_search)
        return found

    def create_rank(self, session, faction=None, rank_number=None, rank_name=None):
        faction = self.find_faction(session, faction)
        rank_number = self.valid['positive_integer'](session, rank_number, thing_name='Faction Rank Number')
        if rank_number in faction.db.rank_names:
            raise AthException("Rank already exists!")
        rank_name = self.valid['word'](session, rank_name, thing_name='Faction Rank Name')
        faction.create_rank(rank_number, rank_name)

    def delete_rank(self, session, faction=None, rank_number=None):
        pass

    def change_rank_title(self, session, faction=None, rank_number=None, new_title=None):
        pass

    def add_member(self, session, faction=None, new_member=None, rank_number=None):
        pass

    def remove_member(self, session, faction=None, member=None):
        pass

    def change_member_rank(self, session, faction=None, member=None, rank_number=None, announce=True):
        pass

    def change_member_title(self, session, faction=None, member=None, new_title=None, announce=True):
        pass


class GroupManager(AthanorScript):

    def at_script_creation(self):
        self.key = "Group Manager"
        self.desc = "Organizes Groups"

    def at_start(self):
        GroupTier.objects.get_or_create(number=0,private=False)
        GroupTier.objects.get_or_create(number=0,private=True)

    def find_tier(self,number,private):
        try:
            number = int(number)
        except:
            raise ValueError("Must enter a Number for tier!")
        private = bool(private)
        tier = GroupTier.objects.filter(number=number,private=private).first()
        if not tier:
            raise ValueError("Tier not found!")
        return tier

    def create_tier(self,number,name,private):
        try:
            number = int(number)
        except:
            raise ValueError("Must enter a Number for tier!")
        name = sanitize_group_name(name)
        private = bool(private)

        if GroupTier.objects.filter(number=number,private=private).count():
            raise ValueError("Tier already exists!")

        if GroupTier.objects.filter(name__iexact=name,private=private).count():
            raise ValueError("Tier name already in use!")

        tier, created = GroupTier.objects.get_or_create(number=number,name=name,private=private)
        return tier

    def rename_tier(self, number, private, new_name):
        tier = self.find_tier(number,private)
        newname = sanitize_group_name(new_name)

        if GroupTier.objects.filter(name__iexact=new_name,private=private).count():
            raise ValueError("Tier name already in use!")

        tier.name = new_name
        tier.save(update_fields=['name'])

    def display(self, viewer, private):
        message = list()
        message.append(viewer.render.header("%s Groups" % "Private" if private else "Public"))
        head_table = viewer.render.make_table(["Name", "Leader", "Second", "Conn"],
                                               header=False, width=[30, 21, 21, 8])
        message.append(head_table)
        for tier in GroupTier.objects.filter(private=private).order('number'):
            message.append(tier.display(viewer,footer=False))
        message.append(viewer.render.footer())
        return message

    def create_group(self, name, tier_number, private):
        name = sanitize_group_name(name)
        tier = self.find_tier(tier_number, private)
        if Group.objects.filter(key__iexact=name).first():
            raise ValueError("Group already exists! Names must be unique.")
        group = Group.objects.create(tier=tier,key=name)
        return group

    def find_group(self, viewer, name, ignore_permissions=False):
        groups = Group.objects.all().order('key')
        if not ignore_permissions:
            groups = [group for group in groups if group.visible_to(viewer)]
        name = sanitize_group_name(name)
        group = partial_match(name, groups)
        if not group:
            raise ValueError("Group '%s' not found!" % name)
        return group

    def rename_group(self, viewer, name, new_name):
        group = self.find_group(viewer, name)
        new_name = sanitize_group_name(new_name)
        exist = Group.objects.filter(key__iexact=new_name).exclude(id=group.id)
        if exist:
            raise ValueError("Group names must be unique!")
        group.key = new_name
        group.save(update_fields=['key'])
        group.setup_channels()

    def change_tier(self, viewer, name, new_tier, private):
        tier = self.find_tier(new_tier, private)
        group = self.find_group(viewer, name)
        group.tier = tier
        group.save(update_fields=['tier'])

    def disband_group(self, viewer, name, confirm_name):
        group = self.find_group(viewer, name)
        confirm_name = sanitize_string(confirm_name)
        if not Group.objects.filter(id=group.id, key__iexact=confirm_name).count():
            raise ValueError("Must enter the group's full case-insensitive name to continue!")
        if not group.check_permission(viewer, 'admin'):
            raise ValueError("Permission denied!")
        group.delete()