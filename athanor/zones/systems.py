import athanor
from athanor.base.systems import AthanorSystem
from athanor.factions.scripts import FactionScript


class FactionSystem(AthanorSystem):
    key = 'faction'
    system_name = 'FACTION'
    load_order = -48
    settings_data = (
        ('faction_locks', 'Default locks for new Factions?', 'lock', ''),
    )

    def base_factions(self):
        return [f for f in FactionScript.objects.filter_family() if f.parent is None]

    def create_faction(self, session, name=None, parent=None):
        pass


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