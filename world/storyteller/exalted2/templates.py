from world.storyteller.templates import Template as OldTemplate
from evennia.utils.ansi import ANSIString
from commands.library import tabular_table

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

    def sheet_advantages(self, owner, width=78):
        colors = self.sheet_colors
        section = list()
        all_charms = sorted([charm for charm in owner.advantages.cache_advantages if charm.base_name == 'Charm'],
                            key=lambda charm2: charm2.full_name)
        charm_types = ['Solar Charms', 'Lunar Charms', 'Abyssal Charms', 'Infernal Charms', 'Terrestrial Charms',
                       'Sidereal Charms', 'Alchemical Charms', 'Jadeborn Patterns', 'Spirit Charms', 'Raksha Charms',
                       'Ghost Arcanoi']
        for charm_type in charm_types:
            section_charms = [charm for charm in all_charms if charm.main_category == charm_type]
            if not section_charms:
                continue
            section.append(self.sheet_header(charm_type, width=width))
            charm_section = list()
            categories = sorted(list(set([charm.sub_category for charm in section_charms])),
                                key=lambda charm2: charm2)
            for category in categories:
                cat_charms = [charm.sheet_format() for charm in section_charms if charm.sub_category == category]
                cat_line = ANSIString('{%s===={n{%s%s{n{%s===={n' % (colors['border'], colors['section_name'], category,
                                                                     colors['border'])).center(width-4, ' ')
                charm_section.append(unicode(cat_line))
                short_charms = [charm for charm in cat_charms if len(charm) <= 36]
                long_charms = [charm for charm in cat_charms if len(charm) > 36]
                if short_charms:
                    charm_section.append(tabular_table(short_charms, field_width=36, line_length=width-2))
                if long_charms:
                    charm_section.append('\n'.join(long_charms))
            section.append(self.sheet_border('\n'.join(charm_section), width=width))

        all_martial = sorted([charm for charm in owner.advantages.cache_advantages if charm.base_name == 'Martial Arts Charm'],
                            key=lambda charm2: charm2.full_name)
        martial_types = ['Terrestrial Martial Arts', 'Celestial Martial Arts', 'Sidereal Martial Arts']

        for martial_type in martial_types:
            charm_section = list()
            section_charms = [charm for charm in all_martial if charm.sub_category == martial_type]
            if not section_charms:
                continue
            section.append(self.sheet_header(martial_type, width=width))
            style_names = sorted(list(set([charm.custom_category for charm in section_charms])))
            for style in style_names:
                style_charms = [charm.sheet_format() for charm in section_charms if charm.custom_category == style]
                cat_line = ANSIString('{%s===={n{%s%s{n{%s===={n' % (colors['border'], colors['section_name'], style,
                                                                     colors['border'])).center(width-4, ' ')
                charm_section.append(unicode(cat_line))
                short_charms = [charm for charm in style_charms if len(charm) <= 36]
                long_charms = [charm for charm in style_charms if len(charm) > 36]
                if short_charms:
                    charm_section.append(tabular_table(short_charms, field_width=36, line_length=width-2))
                if long_charms:
                    charm_section.append('\n'.join(long_charms))
            section.append(self.sheet_border('\n'.join(charm_section), width=width))

        all_spells = sorted([charm for charm in owner.advantages.cache_advantages if charm.base_name == 'Spell'],
                            key=lambda charm2: charm2.full_name)
        spell_types = ['Sorcery', 'Necromancy', 'Protocols']


        for spell_type in spell_types:
            charm_section = list()
            section_charms = [charm for charm in all_spells if charm.sub_category == spell_type]
            if not section_charms:
                continue
            section.append(self.sheet_header(spell_type, width=width))
            category_names = sorted(list(set([charm.custom_category for charm in section_charms])))
            category_names2 = list()

            if spell_type == 'Sorcery':
                if 'Terrestrial Circle Spells' in category_names:
                    category_names2.append('Terrestrial Circle Spells')
                if 'Celestial Circle Spells' in category_names:
                    category_names2.append('Celestial Circle Spells')
                if 'Solar Circle Spells' in category_names:
                    category_names2.append('Solar Circle Spells')
            if spell_type == 'Necromancy':
                if 'Shadowlands Circle Spells' in category_names:
                    category_names2.append('Shadowlands Circle Spells')
                if 'Labyrinth Circle Spells' in category_names:
                    category_names2.append('Labyrinth Circle Spells')
                if 'Void Circle Spells' in category_names:
                    category_names2.append('Void Circle Spells')
            if spell_type == 'Protocols':
                if 'Man-Machine Protocols' in category_names:
                    category_names2.append('Man-Machine Protocols')
                if 'God-machine Protocols' in category_names:
                    category_names2.append('God-machine Protocols')

            for category in category_names2:
                category_spells = [charm.sheet_format() for charm in section_charms if charm.custom_category == category]
                cat_line = ANSIString('{%s===={n{%s%s{n{%s===={n' % (colors['border'], colors['section_name'], category,
                                                                     colors['border'])).center(width-4, ' ')
                charm_section.append(unicode(cat_line))
                short_charms = [charm for charm in category_spells if len(charm) <= 36]
                long_charms = [charm for charm in category_spells if len(charm) > 36]
                if short_charms:
                    charm_section.append(tabular_table(short_charms, field_width=36, line_length=width-2))
                if long_charms:
                    charm_section.append('\n'.join(long_charms))
            section.append(self.sheet_border('\n'.join(charm_section), width=width))



        return section

    def sheet_pools(self, owner, width=78):
        pools = owner.pools.cache_pools
        section = list()
        if not pools:
            return section
        format_pools = [pool.sheet_format() for pool in owner.pools.pools]
        format_channels = [pool.sheet_format() for pool in owner.pools.channels]
        format_tracks = [pool.sheet_format() for pool in owner.pools.tracks]
        section.append(self.sheet_triple_header(['Pools', 'Channels', 'Tracks'], width=width))
        section.append(self.sheet_columns([format_pools, format_channels, format_tracks], width=width))

class Mortal(ExaltedTemplate):
    base_name = 'Mortal'


class Solar(ExaltedTemplate):
    base_name = 'Solar'
    default_pools = UNIVERSAL_POOLS + SOLAR_POOLS
    native_charms = 'Solar'
    sub_class_list = ['Dawn', 'Zenith', 'Eclipse', 'Twilight', 'Night']
    extra_sheet_colors = {'border': 'Y', 'slash': 'r', 'section_name': 'y'}

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
    extra_sheet_colors = {'border': 'C'}

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
