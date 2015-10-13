from world.storyteller.stats import Stat as OldStat, Willpower as OldWillpower, \
    Power as OldPower, Skill as OldSkill, Attribute as OldAttribute

# Define some main categories!


class Willpower(OldWillpower):
    game_category = 'Exalted2'


class Stat(OldStat):
    game_category = 'Exalted2'
    initial_value = 0

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
    always_display = True

class Virtue(Stat):
    main_category = 'Virtue'
    initial_value = 1
    never_display = True

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


# GRACES


class Grace(Stat):
    main_category = 'Grace'
    base_name = 'Grace'


class Heart(Grace):
    base_name = 'Heart'
    list_order = 0


class Cup(Grace):
    base_name = 'Cup'
    list_order = 5


class Sword(Grace):
    base_name = 'Sword'
    list_order = 10


class Staff(Grace):
    base_name = 'Staff'
    list_order = 15


class Ring(Grace):
    base_name = 'Ring'
    list_order = 20


class Way(Grace):
    base_name = 'Way'
    list_order = 25


# COLLEGES


class College(Stat):
    main_category = 'College'
    base_name = 'College'


class TheCorpse(College):
    base_name = 'The Corpse'


class TheCrow(College):
    base_name = 'The Crow'


class TheHaywain(College):
    base_name = 'The Haywain'


class TheRisingSmokee(College):
    base_name = 'The Rising Smoke'


class TheSword(College):
    base_name = 'The Sword'


class TheCaptain(College):
    base_name = 'The Captain'


class TheGull(College):
    base_name = 'The Gull'


class TheMast(College):
    base_name = 'The Mast'


class TheMessenger(College):
    base_name = 'The Messenger'


class TheShipsWheel(College):
    base_name = "The Ship's Wheel"


class TheEwer(College):
    base_name = 'The Ewer'


class TheLovers(College):
    base_name = 'The Lovers'


class TheMusician(College):
    base_name = 'The Musician'


class ThePeacock(College):
    base_name = 'The Peacock'


class ThePillar(College):
    base_name = 'The Pillar'


class TheGuardians(College):
    base_name = 'The Guardians'


class TheKey(College):
    base_name = 'The Key'


class TheMask(College):
    base_name = 'The Mask'


class TheSorcerer(College):
    base_name = 'The Sorcerer'


class TheTreasureTrove(College):
    base_name = 'The Treasure Trove'


class TheBanner(College):
    base_name = 'The Banner'


class TheGauntlet(College):
    base_name = 'The Gauntlet'


class TheQuiver(College):
    base_name = 'The Quiver'


class TheShield(College):
    base_name = 'The Shield'


class TheSpear(College):
    base_name = 'The Spear'


class TheComet(College):
    base_name = 'The Comet'


class TheLightningBolt(College):
    base_name = 'The Lightning Bolt'


# Paths

class Path(Stat):
    main_category = 'Path'
    base_name = 'Path'


class CelestialAir(Path):
    base_name = 'Celestial Air'


class ClearAir(Path):
    base_name = 'Clear Air'


class SolidEarth(Path):
    base_name = 'Solid Earth'


class YieldingEarth(Path):
    base_name = 'Yielding Earth'


class BlazingFire(Path):
    base_name = 'Flickering Fire'


class FlickeringFire(Path):
    base_name = 'Flickering Fire'


class FlowingWater(Path):
    base_name = 'FlowingWater'


class ShimmeringWater(Path):
    base_name = 'Shimmering Water'


class GrowingWood(Path):
    base_name = 'Growing Wood'


class ShapingWood(Path):
    base_name = 'Shaping Wood'


class GloriousConsumption(Path):
    base_name = 'Glorious Consumption'


class CoagulatedEucharist(Path):
    base_name = 'Coagulated Eucharist'


class TechnomorphicTranscendance(Path):
    base_name = 'Technomorphic Transcendance'


class EcstaticArmageddon(Path):
    base_name = 'Ecstatic Armageddon'


class TormentedBodhisattva(Path):
    base_name = 'Tormented Bodhisattva'


# SLOTS

class Slot(Stat):
    main_category = 'Slot'
    base_name = 'Slot'


class General(Slot):
    base_name = 'General'


class Dedicated(Slot):
    base_name = 'Dedicated'



# LISTS

ATTRIBUTES_LIST = [Strength, Dexterity, Stamina, Charisma, Manipulation, Appearance, Perception, Intelligence, Wits]

SKILLS_LIST = [Archery, MartialArts, Melee, Thrown, War, Bureaucracy, Linguistics, Ride, Sail, Socialize, Athletics,
               Awareness, Dodge, Larceny, Stealth, Craft, Investigation, Lore, Medicine, Occult, Integrity,
               Performance, Presence, Resistance, Survival]

VIRTUES_LIST = [Valor, Compassion, Temperance, Conviction]

GRACES_LIST = [Heart, Cup, Sword, Staff, Ring, Way]

COLLEGES_LIST = [TheCorpse, TheCrow, TheHaywain, TheRisingSmokee, TheSword, TheCaptain, TheGull, TheMask, TheMessenger,
                 TheShipsWheel, TheEwer, TheLovers, TheMusician, ThePeacock, ThePillar, TheGuardians, TheKey, TheMask,
                 TheSorcerer, TheTreasureTrove, TheBanner, TheGauntlet, TheQuiver, TheShipsWheel, TheSpear, TheComet,
                 TheLightningBolt]

PATHS_LIST = [CelestialAir, ClearAir, SolidEarth, YieldingEarth, BlazingFire, FlickeringFire, FlowingWater,
              ShimmeringWater, GrowingWood, ShapingWood, GloriousConsumption, CoagulatedEucharist,
              TechnomorphicTranscendance, EcstaticArmageddon, TormentedBodhisattva]

SLOTS_LIST = [General, Dedicated]

MAIN_LIST = [Willpower]

STATS_LIST = MAIN_LIST + ATTRIBUTES_LIST + SKILLS_LIST + VIRTUES_LIST + COLLEGES_LIST + GRACES_LIST + \
             PATHS_LIST + SLOTS_LIST