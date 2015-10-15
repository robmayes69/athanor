from evennia.utils.evtable import EvTable
from evennia.utils.ansi import ANSIString
from commands.library import AthanorError, partial_match, sanitize_string, tabular_table

from world.storyteller.manager import Attributes as OldAttributes, SheetSection, StatSection, Skills as OldSkills, \
    MeritSection, AdvantageStatSection, AdvantageWordSection, FirstSection
from world.storyteller.exalted2.advantages import Charm, Sorcery as SorcerySpell, Necromancy as NecroSpell, \
    Protocol as WeaveSpell, Arts as ThaumArts, Sciences as ThaumSciences, TerrestrialMartialCharm, \
    CelestialMartialCharm, SiderealMartialCharm, SolarCharm, LunarCharm, AbyssalCharm, InfernalCharm, AlchemicalCharm, \
    SiderealCharm, SpiritCharm, RakshaCharm, JadebornCharm, GhostCharm, TerrestrialCharm, Language
from world.storyteller.exalted2.merits import Merit, Flaw, PositiveMutation, NegativeMutation, NeutralMutation, \
    RageMutation, WarformMutation, Background, GodBloodMutation


class Attributes(OldAttributes):
    pass


class Abilities(OldSkills):
    base_name = 'Abilities'
    section_type = 'Ability'


class Backgrounds(MeritSection):
    base_name = 'Backgrounds'
    section_type = 'Background'
    custom_type = Background


class Merits(MeritSection):
    base_name = 'Merits'
    section_type = 'Merit'
    custom_type = Merit
    list_order = 21


class Flaws(MeritSection):
    base_name = 'Flaws'
    section_type = 'Flaw'
    custom_type = Flaw
    list_order = 22


class PositiveMutations(MeritSection):
    base_name = 'PositiveMutations'
    section_type = 'Positive Mutation'
    custom_type = PositiveMutation
    list_order = 23


class NegativeMutations(MeritSection):
    base_name = 'NegativeMutations'
    section_type = 'Negative Mutation'
    custom_type = NegativeMutation
    list_order = 24


class NeutralMutations(MeritSection):
    base_name = 'NeutralMutations'
    section_type = 'Neutral Mutation'
    custom_type = NeutralMutation
    list_order = 25


class RageMutations(MeritSection):
    base_name = 'RageMutations'
    section_type = 'Rage Mutation'
    custom_type = RageMutation
    list_order = 26


class WarformMutations(MeritSection):
    base_name = 'WarformMutations'
    section_type = 'Warform Mutation'
    custom_type = WarformMutation
    list_order = 27


class GodBloodMutations(MeritSection):
    base_name = 'GodBloodMutations'
    section_type = 'God-Blooded Mutation'
    custom_type = GodBloodMutation
    list_order = 28


class SplatCharmSection(AdvantageWordSection):
    base_name = 'DefaultCharms'
    sheet_name = 'Default Charms'
    custom_type = Charm

    def sheet_render(self, width=78):
        section_charms = sorted(self.existing, key=lambda charm2: charm2.full_name)
        if not section_charms:
            return
        colors = self.sheet_colors
        section = list()
        section.append(self.sheet_header(self.sheet_name, width=width))
        charm_section = list()
        categories = sorted(list(set([charm.sub_category for charm in section_charms])),
                            key=lambda category: category)
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
        return '\n'.join(unicode(line) for line in section)


class SolarCharms(SplatCharmSection):
    base_name = 'SolarCharms'
    section_type = 'Solar Charm'
    sheet_name = 'Solar Charms'
    custom_type = SolarCharm
    list_order = 30


class AbyssalCharms(SplatCharmSection):
    base_name = 'AbyssalCharms'
    section_type = 'Abyssal Charm'
    sheet_name = 'Abyssal Charms'
    custom_type = AbyssalCharm
    list_order = 31


class InfernalCharms(SplatCharmSection):
    base_name = 'InfernalCharms'
    section_type = 'Infernal Charm'
    sheet_name = 'Infernal Charms'
    custom_type = InfernalCharm
    list_order = 32


class LunarCharms(SplatCharmSection):
    base_name = 'LunarCharms'
    section_type = 'Lunar Charm'
    sheet_name = 'Lunar Charms'
    custom_type = LunarCharm
    list_order = 33


class SiderealCharms(SplatCharmSection):
    base_name = 'SiderealCharms'
    section_type = 'Sidereal Charm'
    sheet_name = 'Sidereal Charms'
    custom_type = SiderealCharm
    list_order = 34


class TerrestrialCharms(SplatCharmSection):
    base_name = 'TerrestrialCharms'
    section_type = 'Terrestrial Charm'
    sheet_name = 'Terrestrial Charms'
    custom_type = TerrestrialCharm
    list_order = 35


class AlchemicalCharms(SplatCharmSection):
    base_name = 'AlchemicalCharms'
    section_type = 'Alchemical Charm'
    sheet_name = 'Alchemical Charms'
    custom_type = AlchemicalCharm
    list_order = 36


class RakshaCharms(SplatCharmSection):
    base_name = 'RakshaCharms'
    section_type = 'Raksha Charm'
    sheet_name = 'Raksha Charms'
    custom_type = RakshaCharm
    list_order = 37


class JadebornCharms(SplatCharmSection):
    base_name = 'JadebornCharms'
    section_type = 'Jadeborn Charm'
    sheet_name = 'Jadeborn Charms'
    custom_type = JadebornCharm
    list_order = 38


class GhostCharms(SplatCharmSection):
    base_name = 'GhostCharms'
    section_type = 'Ghost Charm'
    sheet_name = 'Ghost Charms'
    custom_type = GhostCharm
    list_order = 39


class SpiritCharms(SplatCharmSection):
    base_name = 'SpiritCharms'
    section_type = 'Spirit Charm'
    sheet_name = 'Spirit Charms'
    custom_type = SpiritCharm
    list_order = 40


class MartialCharms(AdvantageWordSection):
    base_name = 'MartialCharms'

    def sheet_render(self, width=78):
        section_charms = self.existing
        if not section_charms:
            return
        section = list()
        colors = self.sheet_colors
        section.append(self.sheet_header(self.sheet_name, width=width))
        style_names = sorted(list(set([charm.custom_category for charm in section_charms])))
        charm_section = list()
        for style in style_names:
            style_charms = sorted([charm.sheet_format() for charm in section_charms if charm.custom_category == style])
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
        return '\n'.join(unicode(line) for line in section)


class TerrestrialMartialArts(MartialCharms):
    base_name = 'TerrestrialMartialArts'
    section_type = 'Terrestrial Martial Arts Charm'
    sheet_name = 'Terrestrial Martial Arts'
    list_order = 50
    custom_type = TerrestrialMartialCharm


class CelestialMartialArts(MartialCharms):
    base_name = 'CelestialMartialArts'
    section_type = 'Celestial Martial Arts Charm'
    sheet_name = 'Celestial Martial Arts'
    list_order = 51
    custom_type = CelestialMartialCharm


class SiderealMartialArts(MartialCharms):
    base_name = 'SiderealMartialArts'
    section_type = 'Sidereal Martial Arts Charm'
    sheet_name = 'Sidereal Martial Arts'
    list_order = 52
    custom_type = SiderealMartialCharm


class SpellSection(AdvantageWordSection):
    category_listing = list()

    def sheet_render(self, width=78):
        spells = self.existing
        if not spells:
            return
        section = list()
        colors = self.sheet_colors
        section.append(self.sheet_header(self.sheet_name, width=width))
        spell_section = list()
        for category in self.category_listing:
            category_spells = sorted([spell.sheet_format() for spell in spells if spell.sub_category == category],
                                     key=lambda x: x)
            if not category_spells:
                continue
            cat_line = ANSIString('{%s===={n{%s%s{n{%s===={n' % (colors['border'], colors['section_name'], category,
                                                                 colors['border'])).center(width-4, ' ')
            spell_section.append(unicode(cat_line))
            short_charms = [charm for charm in category_spells if len(charm) <= 36]
            long_charms = [charm for charm in category_spells if len(charm) > 36]
            if short_charms:
                spell_section.append(tabular_table(short_charms, field_width=36, line_length=width-2))
            if long_charms:
                spell_section.append('\n'.join(long_charms))
        section.append(self.sheet_border('\n'.join(spell_section), width=width))
        return '\n'.join(unicode(line) for line in section)


class Sorcery(SpellSection):
    base_name = 'Sorcery'
    section_type = 'Sorcery Spells'
    sheet_name = 'Sorcery Spells'
    custom_type = SorcerySpell
    list_order = 60
    category_listing = ['Terrestrial Circle Spells', 'Celestial Circle Spells', 'Solar Circle Spells']


class Necromancy(SpellSection):
    base_name = 'Necromancy'
    section_type = 'Necromancy Spells'
    sheet_name = 'Necromancy Spells'
    custom_type = NecroSpell
    list_order = 61
    category_listing = ['Shadowlands Circle Spells', 'Labyrinth Circle Spells', 'Void Circle Spells']


class Protocols(SpellSection):
    base_name = 'Protocols'
    section_type = 'Weaving Protocols'
    sheet_name = 'Weaving Protocols'
    custom_type = WeaveSpell
    list_order = 62
    category_listing = ['Man-Machine Protocols', 'God-Machine Protocols']


class Languages(AdvantageWordSection):
    base_name = 'Languages'
    section_type = 'Language'
    sheet_name = 'Languages'
    custom_type = Language
    list_order = 80

    def sheet_render(self, width=78):
        languages = self.existing
        if not languages:
            return
        section = list()
        colors = self.sheet_colors
        section.append(self.sheet_header(self.sheet_name, width=width))
        languages_format = ', '.join(sorted([language.sheet_format() for language in languages]))
        section.append(self.sheet_border(languages_format, width=width))
        return '\n'.join(unicode(line) for line in section)


class PoolSection(SheetSection):
    base_name = 'Pools'
    section_type = 'Pool'
    sheet_name = 'Pools'
    use_editchar = False
    list_order = 100

    def load(self):
        self.existing = self.owner.pools.all()
        for pool_type in ['Pool', 'Channel', 'Track']:
            setattr(self, pool_type.lower(), [pool for pool in self.existing if pool.main_category == pool_type])

    def sheet_render(self, width=78):
        pools = self.owner.pools.all()
        section = list()
        if not pools:
            return section
        col_widths = self.calculate_widths(width)
        format_pools = '\n'.join([pool.sheet_format(zfill=3, rjust=col_widths[0]/2) for pool in self.pool])
        format_channels = '\n'.join([pool.sheet_format(zfill=1, rjust=col_widths[1]/2) for pool in self.channel])
        format_tracks = '\n'.join([pool.sheet_format(zfill=2, rjust=col_widths[2]/2) for pool in self.track])
        section.append(self.sheet_triple_header(['Pools', 'Channels', 'Tracks'], width=width))
        section.append(self.sheet_columns([format_pools, format_channels, format_tracks], width=width))
        return '\n'.join(unicode(line) for line in section)



ALL_SECTIONS = [Attributes, Abilities, Backgrounds, Merits, Flaws, PositiveMutations, NegativeMutations,
                NeutralMutations, RageMutations, WarformMutations, GodBloodMutations, SolarCharms, LunarCharms,
                AbyssalCharms, InfernalCharms, SiderealCharms, RakshaCharms, JadebornCharms, GhostCharms, SpiritCharms,
                Sorcery, Necromancy, Protocols, Languages, TerrestrialMartialArts, CelestialMartialArts,
                SiderealMartialArts, PoolSection, FirstSection]
