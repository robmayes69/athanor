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
    kind = 'ability'


class Specialties(OldSpecialties):
    pass


class Favored(OldFavored):
    pass


class Supernal(OldFavored):
    pass


class CharmSection(AdvantageWordSection):
    name = 'Charms'


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


class Sorcery(AdvantageWordSection):
    name = 'Sorcery'
    sub_choices = ('Terrestrial Circle Spells', 'Celestial Circle Spells', 'Solar Circle Spells')


class Necromancy(Sorcery):
    name = 'Necromancy'
    sub_choices = ('Shadowlands Circle Spells', 'Labyrinth Circle Spells', 'Void Circle Spells')


SECTION_LIST = (FirstSection, Attributes, Abilities, Specialties, Favored, Supernal, SolarCharms, AbyssalCharms,
                TerrestrialCharms, MartialCharms, Sorcery, Necromancy)
