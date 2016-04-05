from __future__ import unicode_literals
from commands.library import tabular_table, dramatic_capitalize, partial_match

from world.storyteller.manager import SheetSection, StatSection, Attributes as OldAttributes, Skills, \
    AdvantageStatSection, AdvantageWordSection, Specialties as OldSpecialties, Favored as OldFavored, \
    TemplateSection as OldTemplate, Power


class TemplateSection(OldTemplate):
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
    sub_choices = tuple()
    kind = 'charm'

    def load(self):
        super(CharmSection, self).load()
        self.display_categories = sorted(list(set(stat.sub_category for stat in self.existing)))
        for category in self.display_categories:
            self.charm_categorized[category] = [power for power in self.existing if power.sub_category == category]

    def add(self, sub_category, key, amount=1):
        key = dramatic_capitalize(key)
        found_category = partial_match(sub_category, self.sub_choices)
        if not found_category:
            raise ValueError("'%s' is not a valid category for %s. Choices are: %s" % (sub_category, self.name,
                                                                                       ', '.join(self.sub_choices)))
        try:
            amount = int(amount)
        except ValueError:
            raise ValueError("That isn't an integer!")
        if not amount > 0:
            raise ValueError("%s must be raised by positive numbers.")
        find_power = [power for power in self.existing if power.sub_category == found_category and power.key == key]
        if find_power:
            find_power[0]._rating += amount
            find_power[0].save()
            return
        new_power = Power(key=(self.kind, found_category, key), handler=self.handler)
        self.handler.powers.append(new_power)
        new_power.save()
        self.handler.load_powers()
        self.load()

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
            skill_table = unicode(tabular_table(skill_display, field_width=37, line_length=width-2))
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

SECTION_LIST = (TemplateSection, Attributes, Abilities, Specialties, Favored, Supernal, SolarCharms, AbyssalCharms,
                TerrestrialCharms, MartialCharms, Sorcery, Necromancy)
