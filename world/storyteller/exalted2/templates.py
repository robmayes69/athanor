from world.storyteller.templates import Template as OldTemplate

from world.storyteller.exalted2.stats import Power
from world.storyteller.exalted2.pools import UNIVERSAL_POOLS
from world.storyteller.exalted2.pools import SOLAR_POOLS, INFERNAL_POOLS, ABYSSAL_POOLS


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
    default_pools = []
    native_charms = 'Lunar'
    sub_class_list = ['Full Moon', 'Changing Moon', 'No Moon', 'Waning Moon', 'Half Moon', 'Waxing Moon']


class Sidereal(ExaltedTemplate):
    base_name = 'Sidereal'
    default_pools = []
    native_charms = 'Sidereal'
    sub_class_list = ['Battles', 'Journeys', 'Endings', 'Secrets', 'Serenity']


class Terrestrial(ExaltedTemplate):
    base_name = 'Terrestrial'
    default_pools = []
    native_charms = 'Terrestrial'
    sub_class_list = ['Fire', 'Earth', 'Air', 'Water', 'Wood']
    sub_class_name = 'Aspect'


class Alchemical(ExaltedTemplate):
    base_name = 'Alchemical'
    default_pools = []
    native_charms = 'Alchemical'
    sub_class_name = ['Orichalcum', 'Moonsilver', 'Starmetal', 'Jade', 'Soulsteel']


class Raksha(ExaltedTemplate):
    base_name = 'Raksha'
    default_pools = []
    native_charms = 'Raksha'
    sub_class_name = []


class Jadeborn(ExaltedTemplate):
    base_name = 'Jadeborn'
    default_pools = []
    native_charms = 'Jadeborn'
    sub_class_name = ['Artisan', 'Worker', 'Warrior']


class Ghost(ExaltedTemplate):
    base_name = 'Ghost'
    default_pools = []
    native_charms = 'Ghost'
    sub_class_name = []


class Spirit(ExaltedTemplate):
    base_name = 'Spirit'
    default_pools = []
    native_charms = 'Spirit'
    sub_class_name = ['God', 'Demon', 'Terrestrial']


class GodBlood(ExaltedTemplate):
    base_name = 'God-Blooded'
    sub_class_name = ['Divine', 'Demon', 'Fae', 'Ghost', 'Solar', 'Lunar', 'Sidereal', 'Abyssal', 'Infernal']

    @property
    def default_pools(self):
        return []

    @property
    def native_charms(self):
        return None

TEMPLATES_LIST = [Mortal, Solar, Abyssal, Infernal, Lunar, Sidereal, Terrestrial, Alchemical, Raksha, Jadeborn, Ghost,
                  GodBlood, Spirit]
