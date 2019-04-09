import athanor
from athanor import AthException
from athanor.utils.text import partial_match
from athanor.classes.scripts import AthanorScript


class ZoneScript(AthanorScript):

    def at_script_creation(self):
        self.db.children = set()
        self.tags.add('zone')
        self.db.parent = None

    @property
    def systems(self):
        return athanor.LOADER.systems

    @property
    def parent(self):
        return self.db.parent

    @property
    def children(self):
        return self.db.children

    def add_subzone(self, zone):
        self.db.children.add(zone)
        zone.db.parent = self

    def remove_subzone(self, zone):
        self.db.children.remove(zone)
        zone.db.parent = None

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
