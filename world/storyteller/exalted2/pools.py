from world.storyteller.pools import Pool as OldPool, WillpowerPool as OldWillpowerPool

# Define main types.


class Pool(OldPool):
    game_category = 'Exalted2'


class WillpowerPool(OldWillpowerPool):
    game_category = 'Exalted2'
    list_order = 20

    def retrieve_max(self, owner):
        return int(owner.stats.stats_dict['Willpower'])


class Virtue(Pool):
    main_category = 'Channel'

    def retrieve_max(self, owner):
        return int(owner.stats.stats_dict[self.base_name])


class EssencePool(Pool):
    component_name = 'Mote'
    component_plural = 'Motes'
    value_name = 'Essence'

    def retrieve_stats(self, owner):
        return int(owner.stats.stats_dict['Power']), int(owner.stats.stats_dict['Willpower'])


class PersonalPool(EssencePool):
    base_name = 'Personal'
    value_name = 'Personal Essence'
    list_order = 0


class PeripheralPool(EssencePool):
    base_name = 'Peripheral'
    value_name = 'Peripheral Essence'
    list_order = 5


class ExtendedPool(PeripheralPool):
    base_name = 'Extended'
    value_name = 'Extended Peripheral Essence'
    list_order = 10


class OverdrivePool(EssencePool):
    base_name = 'Overdrive'
    value_name = 'Overdrive Peripheral Essence'
    list_order = 15

    def calculate_overdrive(self, owner):
        pass

    def retrieve_max(self, owner):
        pool_calc = self.calculate_overdrive(owner)
        return sorted([0,pool_calc,25])[1]


class Limit(Pool):
    base_name = 'Limit'
    value_name = 'Limit'
    main_category = 'Track'

    def retrieve_max(self, owner):
        return 10

class ValorPool(Virtue):
    base_name = 'Valor'


class CompassionPool(Virtue):
    base_name = 'Compassion'


class TemperancePool(Virtue):
    base_name = 'Temperance'


class ConvictionPool(Virtue):
    base_name = 'Conviction'


# Solars


class SolarPersonal(PersonalPool):

    def retrieve_max(self, owner):
        power, willpower = self.retrieve_stats(owner)
        return power*3 + willpower

class SolarPeripheral(PeripheralPool):

    def retrieve_max(self, owner):
        power, willpower = self.retrieve_stats(owner)
        virtues = sum(owner.stats.virtue_stats)
        return power*7 + willpower + virtues


class SolarExtended(ExtendedPool):

    def retrieve_max(self, owner):
        return 0


class SolarOverdrive(OverdrivePool):

    def retrieve_max(self, owner):
        return 0

# Abyssals


class AbyssalPersonal(SolarPersonal):
    pass


class AbyssalPeripheral(SolarPeripheral):
    pass


class AbyssalExtended(ExtendedPool):
    pass


class AbyssalOverdrive(OverdrivePool):
    pass


class Resonance(Limit):
    base_name = 'Resonance'

# Infernals


class InfernalPersonal(SolarPersonal):
    pass


class InfernalPeripheral(SolarPeripheral):
    pass


class InfernalExtended(ExtendedPool):
    pass


class InfernalOverdrive(OverdrivePool):
    pass


# Lunars


class LunarPersonal(PersonalPool):
    pass


class LunarPeripheral(PeripheralPool):
    pass


class LunarExtended(ExtendedPool):
    pass


class LunarOverdrive(OverdrivePool):
    pass


# Sidereals


class SiderealPersonal(PersonalPool):
    pass


class SiderealPeripheral(PeripheralPool):
    pass


class SiderealExtended(ExtendedPool):
    pass


class SiderealOverdrive(OverdrivePool):
    pass


class Paradox(Limit):
    value_name = 'Paradox'

# Terrestrial


class TerrestrialPersonal(PersonalPool):
    pass


class TerrestrialPeripheral(PeripheralPool):
    pass


# Alchemical


class AlchemicalPersonal(PersonalPool):
    pass


class AlchemicalPeripheral(PeripheralPool):
    pass


class AlchemicalExtended(ExtendedPool):
    pass


class AlchemicalOverdrive(OverdrivePool):
    pass


class Clarity(Limit):
    value_name = 'Clarity'


class Dissonance(Limit):
    value_name = 'Dissonance'

# Raksha


class RakshaPersonal(PersonalPool):
    pass


class RakshaExtended(ExtendedPool):
    pass


class Stasis(Limit):
    value_name = 'Stasis'


# Spirit


class SpiritPersonal(PersonalPool):

    def retrieve_max(self, owner):
        power = int(owner.stats.stats_dict['Power'])
        return power*10


# Ghost


class GhostPersonal(SpiritPersonal):
    pass


# DragonKing


class DragonKingPersonal(PersonalPool):
    pass


# Jadeborn


class JadebornPersonal(PersonalPool):
    pass

# LISTS

UNIVERSAL_POOLS = [WillpowerPool, ConvictionPool, CompassionPool, ValorPool, TemperancePool]

SOLAR_POOLS = [SolarPersonal, SolarPeripheral, SolarExtended, SolarOverdrive, Limit]
ABYSSAL_POOLS = [AbyssalPersonal, AbyssalPeripheral, AbyssalExtended, AbyssalOverdrive, Resonance]
INFERNAL_POOLS = [InfernalPersonal, InfernalPeripheral, InfernalExtended, InfernalOverdrive, Limit]

LUNAR_POOLS = [LunarPersonal, LunarPeripheral, LunarExtended, LunarOverdrive, Limit]
SIDEREAL_POOLS = [SiderealPersonal, SiderealPeripheral, SiderealExtended, SiderealOverdrive, Limit, Paradox]
TERRESTRIAL_POOLS = [TerrestrialPersonal, TerrestrialPeripheral, Limit]
ALCHEMICAL_POOLS = [AlchemicalPersonal, AlchemicalPeripheral, AlchemicalExtended, AlchemicalOverdrive, Clarity]
RAKSHA_POOLS = [RakshaPersonal, RakshaExtended, Stasis]
SPIRIT_POOLS = [SpiritPersonal]
GHOST_POOLS = [GhostPersonal]
DRAGONKING_POOLS = [DragonKingPersonal]
JADEBORN_POOLS = [JadebornPersonal]

POOL_LIST = set(UNIVERSAL_POOLS + SOLAR_POOLS + ABYSSAL_POOLS + INFERNAL_POOLS + LUNAR_POOLS + SIDEREAL_POOLS + \
            TERRESTRIAL_POOLS + ALCHEMICAL_POOLS + RAKSHA_POOLS + SPIRIT_POOLS + GHOST_POOLS + DRAGONKING_POOLS +
                JADEBORN_POOLS)