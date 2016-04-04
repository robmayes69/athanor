from __future__ import unicode_literals
from commands.library import tabular_table

from world.storyteller.manager import SheetSection, StatSection, Attributes as OldAttributes, Skills, \
    AdvantageStatSection, AdvantageWordSection, Specialties as OldSpecialties, Favored as OldFavored, \
    FirstSection as OldFirst


class FirstSection(OldFirst):
    pass


class Attributes(OldAttributes):
    pass


class Abilities(Skills):
    name = 'Abilities'
    kind = 'ability'


class Specialties(OldSpecialties):
    pass


class Favored(OldFavored):
    pass


class Supernal(OldFavored):
    pass


class CharmSection(AdvantageWordSection):
    name = 'Charms'
    display_categories = tuple()
    charm_categorized = dict()

    def load(self):
        super(CharmSection, self).load()
        self.display_categories = sorted(list(set(stat.sub_category for stat in self.existing)))
        for category in self.display_categories:
            self.charm_categorized[category] = [stat for stat in self.existing if stat.sub_category == category]

    def sheet_render(self, width=78):
        powers = self.existing
        if not powers:
            return
        section = list()
        colors = self.sheet_colors
        section.append(self.sheet_header(self.name, width=width))
        for category in self.display_categories:
            cat_line = '====%s====' % category
            cat_line = cat_line.center(width-2)
            section.append(self.sheet_border(cat_line, width=width))
            skill_display = [power.sheet_format(width=23, colors=colors, mode='word') for power
                             in self.charm_categorized[category]]
            skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
            section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)

class SolarCharms(CharmSection):
    name = 'Solar Charms'
    kind = 'solar_charm'
    sub_choices = ('Archery', 'Brawl', 'Melee', 'War', 'Thrown', 'Bureaucracy', 'Linguistics', 'Ride', 'Sail',
                   'Socialize', 'Athletics', 'Awareness', 'Dodge', 'Larceny', 'Stealth', 'Craft', 'Investigation',
                   'Lore', 'Medicine', 'Occult', 'Integrity', 'Performance', 'Presence', 'Resistance', 'Survival')


class AbyssalCharms(SolarCharms):
    name = 'Abyssal Charms'
    kind = 'abyssal_charm'

class TerrestrialCharms(SolarCharms):
    name = 'Terrestrial Charms'
    kind = 'terrestrial_charm'

class MartialCharms(CharmSection):
    pass


class Sorcery(CharmSection):
    name = 'Sorcery'
    sub_choices = ('Terrestrial Circle Spells', 'Celestial Circle Spells', 'Solar Circle Spells')
    kind = 'sorcery_spell'

class Necromancy(Sorcery):
    name = 'Necromancy'
    sub_choices = ('Shadowlands Circle Spells', 'Labyrinth Circle Spells', 'Void Circle Spells')
    kind = 'necromancy_spell'

SECTION_LIST = (FirstSection, Attributes, Abilities, Specialties, Favored, Supernal, SolarCharms, AbyssalCharms,
                TerrestrialCharms, MartialCharms, Sorcery, Necromancy)
