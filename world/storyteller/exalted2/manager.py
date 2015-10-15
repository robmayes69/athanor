from evennia.utils.evtable import EvTable
from evennia.utils.ansi import ANSIString
from commands.library import AthanorError, partial_match, sanitize_string, tabular_table

from world.storyteller.manager import Attributes as OldAttributes, SheetSection, StatSection, Skills as OldSkills, \
    MeritSection, AdvantageStatSection, AdvantageWordSection
from world.storyteller.exalted2.advantages import Charm, Sorcery, Necromancy, Protocol, MartialCharm, Thaumaturgy, \
    SolarCharm, LunarCharm, AbyssalCharm, InfernalCharm, AlchemicalCharm, SiderealCharm, SpiritCharm, RakshaCharm, \
    JadebornCharm, GhostCharm, TerrestrialCharm
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
        section_charms = sorted(self.existing, key=lambda charm: charm.full_name)
        if not section_charms:
            return
        colors = self.sheet_colors
        section = list()
        section.append(self.sheet_header(self.sheet_name, width=width))
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
        return '\n'.join(unicode(line) for line in section)


class SolarCharms(SplatCharmSection):
    base_name = 'SolarCharms'
    sheet_name = 'Solar Charms'
    custom_type = SolarCharm

ALL_SECTIONS = [Attributes, Abilities, Backgrounds, Merits, Flaws, PositiveMutations, NegativeMutations,
                NeutralMutations, RageMutations, WarformMutations, GodBloodMutations, SolarCharms]
