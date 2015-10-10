from world.storyteller.templates import Template as OldTemplate

from world.storyteller.exalted2.stats import Power
from world.storyteller.exalted2.pools import UNIVERSAL_POOLS
from world.storyteller.exalted2.pools import SOLAR_POOLS, INFERNAL_POOLS, ABYSSAL_POOLS, LUNAR_POOLS, SIDEREAL_POOLS
from world.storyteller.exalted2.pools import TERRESTRIAL_POOLS, ALCHEMICAL_POOLS, RAKSHA_POOLS, DRAGONKING_POOLS
from world.storyteller.exalted2.pools import SPIRIT_POOLS, GHOST_POOLS, JADEBORN_POOLS


class ExaltedTemplate(OldTemplate):
    game_category = 'Exalted2'
    default_pools = UNIVERSAL_POOLS
    native_charms = None
    power_stat = Power
    sub_class_name = 'Caste'


class Mortal(ExaltedTemplate):
    base_name = 'Mortal'


class Solar(ExaltedTemplate):
    base_name = 'Solar'
    default_pools = UNIVERSAL_POOLS + SOLAR_POOLS
    native_charms = 'Solar'
    sub_class_list = ['Dawn', 'Zenith', 'Eclipse', 'Twilight', 'Night']


class Abyssal(Solar):
    base_name = 'Abyssal'
    default_pools = UNIVERSAL_POOLS + ABYSSAL_POOLS
    native_charms = 'Abyssal'
    sub_class_list = ['Dusk', 'Midnight', 'Moonshadow', 'Daybreak', 'Day']


class Infernal(ExaltedTemplate):
    base_name = 'Infernal'
    default_pools = UNIVERSAL_POOLS + INFERNAL_POOLS
    native_charms = 'Infernal'
    sub_class_list = ['Slayer', 'Malefactor', 'Fiend', 'Defiler', 'Scourge']


class Lunar(ExaltedTemplate):
    base_name = 'Lunar'
    default_pools = UNIVERSAL_POOLS + LUNAR_POOLS
    native_charms = 'Lunar'
    sub_class_list = ['Full Moon', 'Changing Moon', 'No Moon', 'Waning Moon', 'Half Moon', 'Waxing Moon']


class Sidereal(ExaltedTemplate):
    base_name = 'Sidereal'
    default_pools = UNIVERSAL_POOLS + SIDEREAL_POOLS
    native_charms = 'Sidereal'
    sub_class_list = ['Battles', 'Journeys', 'Endings', 'Secrets', 'Serenity']


class Terrestrial(ExaltedTemplate):
    base_name = 'Terrestrial'
    default_pools = UNIVERSAL_POOLS + TERRESTRIAL_POOLS
    native_charms = 'Terrestrial'
    sub_class_list = ['Fire', 'Earth', 'Air', 'Water', 'Wood']
    sub_class_name = 'Aspect'


class Alchemical(ExaltedTemplate):
    base_name = 'Alchemical'
    default_pools = UNIVERSAL_POOLS + ALCHEMICAL_POOLS
    native_charms = 'Alchemical'
    sub_class_list = ['Orichalcum', 'Moonsilver', 'Starmetal', 'Jade', 'Soulsteel']


class Raksha(ExaltedTemplate):
    base_name = 'Raksha'
    default_pools = UNIVERSAL_POOLS + RAKSHA_POOLS
    native_charms = 'Raksha'
    sub_class_list = []


class Jadeborn(ExaltedTemplate):
    base_name = 'Jadeborn'
    default_pools = UNIVERSAL_POOLS + JADEBORN_POOLS
    native_charms = 'Jadeborn'
    sub_class_list = ['Artisan', 'Worker', 'Warrior']


class DragonKing(ExaltedTemplate):
    base_name = 'Dragon-King'
    default_pools = UNIVERSAL_POOLS + DRAGONKING_POOLS
    native_charms = None
    sub_class_name = 'Breed'
    sub_class_list = ['Anklok', 'Mosok', 'Pterok', 'Raptok']


class Ghost(ExaltedTemplate):
    base_name = 'Ghost'
    default_pools = UNIVERSAL_POOLS + GHOST_POOLS
    native_charms = 'Ghost'
    sub_class_list = []


class Spirit(ExaltedTemplate):
    base_name = 'Spirit'
    default_pools = UNIVERSAL_POOLS + SPIRIT_POOLS
    native_charms = 'Spirit'
    sub_class_list = ['God', 'Demon', 'Terrestrial']


class GodBlood(ExaltedTemplate):
    base_name = 'God-Blooded'
    sub_class_list = ['Divine', 'Demon', 'Fae', 'Ghost', 'Solar', 'Lunar', 'Sidereal', 'Abyssal', 'Infernal']

    @property
    def default_pools(self):
        return []

    @property
    def native_charms(self):
        return None

TEMPLATES_LIST = [Mortal, Solar, Abyssal, Infernal, Lunar, Sidereal, Terrestrial, Alchemical, Raksha, Jadeborn, Ghost,
                  GodBlood, Spirit, DragonKing]
