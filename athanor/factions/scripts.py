import athanor
from athanor import AthException
from athanor.utils.text import partial_match
from athanor.classes.scripts import AthanorScript


class FactionScript(AthanorScript):
    all_permissions = set()
    system_ranks = {1, 2, 3, 4}
    settings_data = (
        ('color', 'Color to display the faction in!', 'color', 'n'),
        ('private', 'Whether this faction is Private or not.', 'bool', True),
        ('start_rank', 'Default starting rank of new members.', 'positive_integer', 4),
        ('')

    )

    def at_script_creation(self):
        self.db.children = set()
        self.tags.add('faction')
        self.db.members = set()
        self.db.leadership = dict()
        self.db.ranks_held = dict()
        self.db.rank_permissions = dict()
        self.db.titles = dict()
        self.db.rank_names = {
            1: 'Leader',
            2: 'Second in Command',
            3: 'Officer',
            4: 'Member',
        }
        self.db.base_permissions = set()
        self.db.member_permissions = dict()
        self.db.category = 'Uncategorized'

    @property
    def systems(self):
        return athanor.LOADER.systems

    @property
    def parent(self):
        return self.db.parent

    @property
    def children(self):
        return self.db.children

    def add_subfaction(self, faction):
        self.db.children.add(faction)
        faction.db.parent = self

    def remove_subfaction(self, faction):
        self.db.children.remove(faction)
        faction.db.parent = None

    def add_member(self, character):
        self.db.members.add(character)
        if not isinstance(character.db.factions, set):
            character.db.factions = set()
        character.db.factions.add(self)

    def remove_member(self, character):
        if character in self.db.titles:
            del self.db.titles[character]
        rank = self.db.ranks_held.get(character, None)
        if rank is not None:
            if rank in self.db.leadership:
                self.db.leadership[rank].remove(character)
            del self.db.ranks_held[character]
        self.db.members.remove(character)
        if isinstance(character.db.factions, set):
            character.db.factions.remove(self)

    def find_child(self, search_text):
        next_search = None
        if not search_text:
            raise AthException("No search text!")
        if '/' in search_text:
            search_text, next_search = search_text.split('/', 1)
        found = partial_match(search_text, self.children)
        if found and next_search:
            return found.find_child(next_search)
        return found

    def create_rank(self, rank_number, rank_name):
        self.db.rank_names[rank_number] = rank_name
        self.db.rank_permissions[rank_number] = set()
        self.db.leadership[rank_number] = set()
