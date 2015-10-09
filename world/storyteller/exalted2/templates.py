from world.storyteller.templates import Template as OldTemplate

from world.storyteller.exalted2.stats import Power
from world.storyteller.exalted2.pools import WillpowerPool, Limit, Resonance
from world.storyteller.exalted2.pools import SolarPersonal, SolarPeripheral, SolarExtended, SolarOverdrive
from world.storyteller.exalted2.pools import AbyssalPersonal, AbyssalPeripheral, AbyssalExtended, AbyssalOverdrive
from world.storyteller.exalted2.pools import InfernalPersonal, InfernalPeripheral, InfernalExtended, InfernalOverdrive

class ExaltedTemplate(OldTemplate):
    game_category = 'Exalted2'
    default_pools = []
    native_charms = None
    power_stat = Power


class Mortal(ExaltedTemplate):
    base_name = 'Mortal'
    default_pools = [WillpowerPool]


class Solar(ExaltedTemplate):
    base_name = 'Solar'
    default_pools = [WillpowerPool, Limit, SolarPeripheral, SolarPersonal, SolarExtended, SolarOverdrive]
    native_charms = 'Solar'
    sub_class_list = ['Dawn', 'Zenith', 'Eclipse', 'Twilight', 'Night']


class Abyssal(Solar):
    base_name = 'Abyssal'
    default_pools = [WillpowerPool, Resonance, AbyssalPersonal, AbyssalPeripheral, AbyssalExtended, AbyssalOverdrive]
    native_charms = 'Abyssal'
    sub_class_list = ['Dusk', 'Midnight', 'Moonshadow', 'Daybreak', 'Day']


class Infernal(ExaltedTemplate):
    base_name = 'Infernal'
    default_pools = [WillpowerPool, Resonance, InfernalPersonal, InfernalPeripheral,
                     InfernalExtended, InfernalOverdrive]
    native_charms = 'Infernal'
    sub_class_list = ['Slayer', 'Malefactor', 'Fiend', 'Defiler', 'Scourge']


TEMPLATES_LIST = [Mortal, Solar, Abyssal, Infernal]