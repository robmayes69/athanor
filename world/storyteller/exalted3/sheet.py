from __future__ import unicode_literals

from world.storyteller.manager import SheetSection, StatSection, Attributes as OldAttributes, Skills, \
    AdvantageStatSection, AdvantageWordSection, Specialties as OldSpecialties, Favored as OldFavored, \
    FirstSection as OldFirst


class FirstSection(OldFirst):
    pass


class Attributes(OldAttributes):
    pass


class Abilities(Skills):
    name = 'Abilities'

    def load(self):
        self.choices = self.owner.ndb.stats_type['ability']
