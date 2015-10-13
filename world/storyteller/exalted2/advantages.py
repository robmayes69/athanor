from world.storyteller.advantages import WordPower


class Charm(WordPower):
    base_name = 'Charm'

    def __repr__(self):
        return '<%s: %s - (%s)>' % (self.main_category, self.full_name, self.display_rank)

# Solar Charms


class SolarCharm(Charm):
    main_category = 'Solar Charms'
    available_subcategories = ['Archery', 'Martial Arts', 'Melee', 'Thrown', 'War', 'Linguistics', 'Ride', 'Sail',
                               'Socialize', 'Athletics', 'Awareness', 'Dodge', 'Larceny', 'Stealth', 'Craft',
                               'Investigation', 'Lore', 'Medicine', 'Occult', 'Integrity', 'Performance', 'Presence',
                               'Resistance', 'Survival']


class AbyssalCharm(SolarCharm):
    main_category = 'Abyssal Charms'


class SiderealCharm(SolarCharm):
    main_category = 'Sidereal Charms'


class TerrestrialCharm(SolarCharm):
    main_category = 'Terrestrial Charms'


class LunarCharm(Charm):
    main_category = 'Lunar Charms'
    available_subcategories = ['Strength', 'Dexterity', 'Stamina', 'Charisma', 'Manipulation', 'Appearance',
                               'Intelligence', 'Perception', 'Wits', 'Knacks']


class InfernalCharm(Charm):
    main_category = 'Infernal Charms'
    available_subcategories = ['Malfeas', 'Cecelyne', 'SWLiHN', 'Adorjan', 'The Ebon Dragon', 'Kimbery', 'Theion',
                               'Heretical', 'Martial Arts', 'Hegra']


class AlchemicalCharm(Charm):
    main_category = 'Alchemical Charms'
    available_subcategories = ['Combat', 'Survival', 'Speed and Mobility', 'Social', 'Stealth and Disguise',
                               'Analytic and Cognitive', 'Labor and Utility', 'Submodules', 'General', 'Mass Combat',
                               'Spiritual']



class RakshaCharm(Charm):
    main_category = 'Raksha Charms'
    available_subcategories = ['Mask', 'Heart', 'Cup', 'Ring', 'Staff', 'Sword', 'Way']


class SpiritCharm(Charm):
    main_category = 'Spirit Charms'
    available_subcategories = ['General', 'Universal', 'Aegis', 'Blessings', 'Curses', 'Divinations', 'Divine Works',
                               'Edges', 'Eidola', 'Enchantments', 'Inhabitings', 'Relocations', 'Sendings', 'Tantra']


class GhostCharm(Charm):
    main_category = 'Ghost Arcanoi'
    available_subcategories = ['Universal']


class JadebornCharm(Charm):
    main_category = 'Jadeborn Patterns'
    available_subcategories = ['Foundation', 'Worker', 'Warrior', 'Artisan', 'Enlightened', 'Chaos']


class Spell(WordPower):
    base_name = 'DefaultSpell'


class Sorcery(Spell):
    main_category = 'Sorcery'
    available_subcategories = ['Terrestrial Circle Spells', 'Celestial Circle Spells', 'Solar Circle Spells']

class Necromancy(Spell):
    main_category = 'Necromancy'
    available_subcategories = ['Shadowlands Circle Spells', 'Labyrinth Circle Spells', 'Void Circle Spells']


class Thaumaturgy(WordPower):
    main_category = 'Thaumaturgy'
    available_subcategories = ['Arts Degrees', 'Arts Procedures', 'Sciences Degrees', 'Sciences Procedures']


class MartialCharm(Charm):
    main_category = 'Martial Arts'
    available_subcategories = ['Terrestrial Martial Arts', 'Celestial Martial Arts', 'Sidereal Martial Arts']


ALL_WORDPOWERS = SolarCharm + LunarCharm + AbyssalCharm + InfernalCharm + SiderealCharm + TerrestrialCharm + \
                 AlchemicalCharm + RakshaCharm + SpiritCharm + GhostCharm + JadebornCharm + Sorcery + Necromancy + \
                 Thaumaturgy + MartialCharm