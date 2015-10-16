
from django.conf import settings
from world.storyteller.pools import Pool as OldPool, WillpowerPool as OldWillpowerPool

# Define main types.


class Pool(OldPool):
    game_category = 'Exalted2'


class WillpowerPool(OldWillpowerPool):
    game_category = 'Exalted2'
    list_order = 20

    def retrieve_max(self, owner):
        return int(owner.stats.get('Willpower'))


class Virtue(Pool):
    main_category = 'Channel'

    def retrieve_max(self, owner):
        return int(owner.stats.get(self.base_name))


class EssencePool(Pool):
    component_name = 'Mote'
    component_plural = 'Motes'
    value_name = 'Essence'

    def retrieve_stats(self, owner):
        if settings.EX2_POOL_MAX_VIRTUES:
            virtues = [5, 5, 5, 5]
        else:
            virtues = owner.stats.category('Virtue')
        if settings.EX2_POOL_MAX_WILLPOWER:
            willpower = 10
        else:
            willpower = int(owner.stats.get('Willpower'))
        power = int(owner.stats.get('Power'))
        return power, willpower, virtues


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

    def retrieve_max(self, owner):
        extended_charms = owner.template.template.extended_charms
        if not extended_charms:
            return 0
        total_extended = list()
        for worth, charm_names in extended_charms.items():
            found_values = sum([charm.current_value for charm in owner.advantages.cache_advantages
                                if charm.base_name == 'Charm' and charm.full_name in charm_names])
            if found_values:
                total_extended.append(found_values * worth)
        return sum(total_extended)

class OverdrivePool(EssencePool):
    base_name = 'Overdrive'
    value_name = 'Overdrive Peripheral Essence'
    list_order = 15

    def calculate_overdrive(self, owner):
        overdrive_charms = owner.template.template.overdrive_charms
        if not overdrive_charms:
            return 0
        total_overdrive = list()
        for worth, charm_names in overdrive_charms.items():
            found_values = sum([charm.current_value for charm in owner.advantages.cache_advantages
                                if charm.base_name == 'Charm' and charm.full_name in charm_names])
            if found_values:
                total_overdrive.append(found_values * worth)
        return sum(total_overdrive)

    def retrieve_max(self, owner):
        pool_calc = self.calculate_overdrive(owner)
        return sorted([0, pool_calc, 25])[1]


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
        power, willpower, virtues = self.retrieve_stats(owner)
        return power*3 + willpower


class SolarPeripheral(PeripheralPool):

    def retrieve_max(self, owner):
        power, willpower, virtues, = self.retrieve_stats(owner)
        return power*7 + willpower + sum(virtues)


class SolarExtended(ExtendedPool):
    pass


class SolarOverdrive(OverdrivePool):
    pass

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

    def retrieve_max(self, owner):
        power, willpower, virtues = self.retrieve_stats(owner)
        return power + willpower*2


class LunarPeripheral(PeripheralPool):

    def retrieve_max(self, owner):
        power, willpower, virtues = self.retrieve_stats(owner)
        virtue = int(max(virtues))
        return power*4 + willpower*2 + virtue*4


class LunarExtended(ExtendedPool):
    pass


class LunarOverdrive(OverdrivePool):
    pass


# Sidereals


class SiderealPersonal(PersonalPool):

    def retrieve_max(self, owner):
        power, willpower, virtues = self.retrieve_stats(owner)
        return power*2 + willpower


class SiderealPeripheral(PeripheralPool):

    def retrieve_max(self, owner):
        power, willpower, virtues = self.retrieve_stats(owner)
        virtues = sum(virtues)
        return power*6 + willpower + virtues


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


# Spirit


class SpiritPersonal(PersonalPool):

    def retrieve_max(self, owner):
        power = int(owner.stats.get('Power'))
        return power*10


# Raksha


class RakshaPersonal(SpiritPersonal):
    pass


class RakshaExtended(ExtendedPool):
    pass


class Stasis(Limit):
    value_name = 'Stasis'


# Ghost


class GhostPersonal(SpiritPersonal):
    pass


# DragonKing


class DragonKingPersonal(PersonalPool):

    def retrieve_max(self, owner):
        power, willpower, virtues = self.retrieve_stats(owner)
        if settings.EX2_POOL_MAX_VIRTUES:
            virtues2 = 10
        else:
            virtues2 = sum(owner.stats.get('Conviction'), owner.stats.get('Valor'))
        return power*4 + willpower*2 + virtues2


# Jadeborn


class JadebornPersonal(RakshaPersonal):
    pass


# Mortal


class MortalPersonal(SpiritPersonal):
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
MORTAL_POOLS = [MortalPersonal]

POOL_LIST = list(set(UNIVERSAL_POOLS + SOLAR_POOLS + ABYSSAL_POOLS + INFERNAL_POOLS + LUNAR_POOLS + SIDEREAL_POOLS + \
            TERRESTRIAL_POOLS + ALCHEMICAL_POOLS + RAKSHA_POOLS + SPIRIT_POOLS + GHOST_POOLS + DRAGONKING_POOLS + \
                JADEBORN_POOLS + MORTAL_POOLS))
