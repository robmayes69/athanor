from world.storyteller.stats import Stat as OldStat, Willpower as OldWillpower, \
    Power as OldPower, Skill as OldSkill, Attribute as OldAttribute

# Define some main categories!


class Willpower(OldWillpower):
    game_category = 'Exalted2'


class Stat(OldStat):
    game_category = 'Exalted2'


class Power(OldPower):
    game_category = 'Exalted2'
    custom_name = 'Essence'


class Skill(OldSkill):
    game_category = 'Exalted2'
    can_specialize = True
    can_favor = True

class Attribute(OldAttribute):
    game_category = 'Exalted2'
    can_specialize = True
    can_favor = True


class Virtue(Stat):
    main_category = 'Virtue'
    initial_value = 1

# Define Attribute categories.


class PhysicalAttribute(Attribute):
    sub_category = 'Physical'


class SocialAttribute(Attribute):
    sub_category = 'Social'


class MentalAttribute(Attribute):
    sub_category = 'Mental'


# Define Attributes.


class Strength(PhysicalAttribute):
    base_name = 'Strength'
    list_order = 1


class Dexterity(PhysicalAttribute):
    base_name = 'Dexterity'
    list_order = 2


class Stamina(PhysicalAttribute):
    base_name = 'Stamina'
    list_order = 3


class Charisma(SocialAttribute):
    base_name = 'Charisma'
    list_order = 4


class Manipulation(SocialAttribute):
    base_name = 'Manipulation'
    list_order = 5


class Appearance(SocialAttribute):
    base_name = 'Appearance'
    list_order = 6


class Perception(MentalAttribute):
    base_name = 'Perception'
    list_order = 7


class Intelligence(MentalAttribute):
    base_name = 'Intelligence'
    list_order = 8


class Wits(MentalAttribute):
    base_name = 'Wits'
    list_order = 9

# Define Abilities


class Archery(Skill):
    base_name = 'Archery'
    list_order = 10


class MartialArts(Skill):
    base_name = 'Martial Arts'
    list_order = 15


class Melee(Skill):
    base_name = 'Melee'
    list_order = 20


class Thrown(Skill):
    base_name = 'Thrown'
    list_order = 25


class War(Skill):
    base_name = 'War'
    list_order = 30


class Bureaucracy(Skill):
    base_name = 'Bureaucracy'
    list_order = 35


class Linguistics(Skill):
    base_name = 'Linguistics'
    list_order = 40


class Ride(Skill):
    base_name = 'Ride'
    list_order = 45


class Sail(Skill):
    base_name = 'Sail'
    list_order = 50


class Socialize(Skill):
    base_name = 'Socialize'
    list_order = 55


class Athletics(Skill):
    base_name = 'Athletics'
    list_order = 60


class Awareness(Skill):
    base_name = 'Awareness'
    list_order = 65


class Dodge(Skill):
    base_name = 'Dodge'
    list_order = 70


class Larceny(Skill):
    base_name = 'Larceny'
    list_order = 75


class Stealth(Skill):
    base_name = 'Stealth'
    list_order = 80


class Craft(Skill):
    base_name = 'Craft'
    list_order = 85


class Investigation(Skill):
    base_name = 'Investigation'
    list_order = 90


class Lore(Skill):
    base_name = 'Lore'
    list_order = 95


class Medicine(Skill):
    base_name = 'Medicine'
    list_order = 100


class Occult(Skill):
    base_name = 'Occult'
    list_order = 105


class Integrity(Skill):
    base_name = 'Integrity'
    list_order = 110


class Performance(Skill):
    base_name = 'Performance'
    list_order = 115


class Presence(Skill):
    base_name = 'Presence'
    list_order = 120


class Resistance(Skill):
    base_name = 'Resistance'
    list_order = 125


class Survival(Skill):
    base_name = 'Survival'
    list_order = 130


# VIRTUES


class Valor(Virtue):
    base_name = 'Valor'
    list_order = 0


class Compassion(Virtue):
    base_name = 'Compassion'
    list_order = 5


class Temperance(Virtue):
    base_name = 'Temperance'
    list_order = 10


class Conviction(Virtue):
    base_name = 'Conviction'
    list_order = 15


# LISTS

ATTRIBUTES_LIST = [Strength, Dexterity, Stamina, Charisma, Manipulation, Appearance, Perception, Intelligence, Wits]

SKILLS_LIST = [Archery, MartialArts, Melee, Thrown, War, Bureaucracy, Linguistics, Ride, Sail, Socialize, Athletics,
               Awareness, Dodge, Larceny, Stealth, Craft, Investigation, Lore, Medicine, Occult, Integrity,
               Performance, Presence, Resistance, Survival]

VIRTUES_LIST = [Valor, Compassion, Temperance, Conviction]

MAIN_LIST = []

STATS_LIST = MAIN_LIST + ATTRIBUTES_LIST + SKILLS_LIST + VIRTUES_LIST