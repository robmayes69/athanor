from __future__ import unicode_literals

import math
from django.conf import settings
from evennia.utils.evtable import EvTable
from evennia.utils.ansi import ANSIString
from commands.library import partial_match, sanitize_string, tabular_table, dramatic_capitalize
from evennia.utils.utils import make_iter

class SheetSection(object):
    name = 'DefaultSection'
    list_order = 0
    sheet_display = True
    handler = None
    kind = 'sheet'

    def __init__(self, handler):
        self.handler = handler
        self.owner = handler.owner
        self.colors = self.sheet_colors
        self.load()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<SheetSection: %s>' % self.name

    def load(self):
        pass

    def sheet_render(self, width=78):
        return None

    @property
    def sheet_colors(self):
        color_dict = dict()
        color_dict.update(self.owner.storyteller.base_sheet_colors)
        color_dict.update(self.owner.storyteller.extra_sheet_colors)
        return color_dict

    def sheet_header(self, center_text=None, width=78):
        colors = self.colors
        start_char = ANSIString('{%s}{n' % colors['border'])
        end_char = ANSIString('{%s{{{n' % colors['border'])
        if not center_text:
            center_section = '-' * (width - 2)
            center_section = ANSIString('{%s%s{n' % (colors['border'], center_section))
        else:
            show_width = width - 2
            fill = ANSIString('{%s-{n' % colors['border'])
            center_section = ANSIString('{%s/{n{%s%s{n{%s/{n' % (colors['slash'], colors['section_name'], center_text,
                                                                 colors['slash'])).center(show_width, fill)
        return start_char + center_section + end_char

    def sheet_triple_header(self, display_text=None, width=78):
        if not display_text:
            display_text = ['', '', '']
        colors = self.colors
        col_widths = self.calculate_widths(width-2)
        fill = ANSIString('{%s-{n' % colors['border'])
        sections = list()
        for count, header in enumerate(display_text):
            center_text = ANSIString('{%s/{n{%s%s{n{%s/{n' % (colors['slash'], colors['section_name'], header,
                                                              colors['slash'])).center(col_widths[count], fill)
            sections.append(center_text)

        start_char = ANSIString('{%s}{n' % colors['border'])
        end_char = ANSIString('{%s{{{n' % colors['border'])
        return start_char + sections[0] + sections[1] + sections[2] + end_char

    def sheet_border(self, display_text=None, width=78):
        colors = self.colors
        ev_table = EvTable(border='cols', pad_width=0, valign='t',
                           border_left_char=ANSIString('{%s|{n' % colors['border']),
                           border_right_char=ANSIString('{%s|{n' % colors['border']), header=False)
        ev_table.add_row(display_text, width=width)
        return ev_table

    def sheet_columns(self, display_text=None, width=78):
        if not display_text:
            display_text = ['', '', '']
        colors = self.colors
        ev_table = EvTable(border='cols', pad_width=0, valign='t',
                           border_left_char=ANSIString('{%s|{n' % colors['border']),
                           border_right_char=ANSIString('{%s|{n' % colors['border']), header=False)
        ev_table.add_row(display_text[0], display_text[1], display_text[2])

        for count, col_width in enumerate(self.calculate_widths(width=width)):
            ev_table.reformat_column(count, width=col_width)
        return ev_table

    def sheet_two_columns(self, display_text=None, width=78):
        if not display_text:
            display_text = ['', '']
        colors = self.colors
        ev_table = EvTable(border='cols', pad_width=0, valign='t',
                           border_left_char=ANSIString('{%s|{n' % colors['border']),
                           border_right_char=ANSIString('{%s|{n' % colors['border']), header=False)
        ev_table.add_row(display_text[0], display_text[1])

        for count, col_width in enumerate(self.calculate_double(width=width)):
            ev_table.reformat_column(count, width=col_width)
        return ev_table

    def calculate_widths(self, width=78):
        column_widths = list()
        col_calc = width / float(3)
        for num in [0, 1, 2]:
            if num == 0:
                calculate = int(math.floor(col_calc))
                column_widths.append(calculate)
            if num == 1:
                calculate = int(math.ceil(col_calc))
                column_widths.append(calculate)
            if num == 2:
                calculate = int(width - 0 - column_widths[0] - column_widths[1])
                column_widths.append(calculate)
        return column_widths

    def calculate_double(self, width=78):
        column_widths = list()
        col_calc = width / float(2)
        for num in [0, 1]:
            if num == 0:
                calculate = int(math.floor(col_calc))
                column_widths.append(calculate)
            if num == 1:
                calculate = int(math.ceil(col_calc))
                column_widths.append(calculate)
        return column_widths


class StatSection(SheetSection):
    choices = tuple()
    kind = 'stat'

    def load(self):
        self.choices = [stat for stat in self.handler.stats_dict.values() if stat.kind == self.kind]

    def set(self, skill, rating):
        found_stat = partial_match(skill, self.choices)
        if not found_stat:
            raise ValueError("Cannot find '%s'. Your choices are: %s" % (skill,
                                                                         ', '.join(str(stat) for stat in self.choices)))
        try:
            rating = int(rating)
        except ValueError:
            raise ValueError("Rating must be a number!")
        found_stat.rating = rating
        found_stat.save()

    def all(self):
        return self.choices

class CustomSection(StatSection):
    kind = 'custom'

    def load(self):
        self.existing = sorted([stat for stat in self.owner.storyteller.customs.all() if stat.stat.kind.key == self.kind],
                               key=lambda stat2: str(stat2))

    def set(self, skill, rating):
        try:
            rating = int(rating)
        except ValueError:
            raise ValueError("That's not an acceptable rating!")
        find_stat = partial_match(skill, self.existing)
        if not find_stat:
            game = self.owner.storyteller.game
            custom = game.custom_stats.filter(key=self.kind).first()
            make_stat, created = custom.custom_stats.get_or_create(key=dramatic_capitalize(skill))
            find_stat, created2 = make_stat.characters.get_or_create(character=self.owner.storyteller)
        if rating > 0:
            find_stat.rating = rating
            find_stat.save()
        else:
            find_stat.delete()
        self.load()

    def sheet_render(self, width=78):
        colors = self.sheet_colors
        skills = [stat for stat in self.existing if stat.display()]
        if not skills:
            return
        section = list()
        section.append(self.sheet_header(self.name, width=width))
        skill_display = [stat.sheet_format(width=24, colors=colors) for stat in skills]
        skill_table = tabular_table(skill_display, field_width=24, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)


class Attributes(StatSection):
    name = 'Attributes'
    list_order = 10
    physical = tuple()
    social = tuple()
    mental = tuple()
    kind = 'attribute'

    def load(self):
        self.choices = sorted([stat for stat in self.handler.stats_type[self.kind] if stat.kind == self.kind],
                              key=lambda stat2: stat2.list_order)
        for stat_type in ['Physical', 'Social', 'Mental']:
            setattr(self, stat_type.lower(), [stat for stat in self.choices if stat.category == stat_type])

    def sheet_render(self, width=78):
        colors = self.colors
        section = list()
        section.append(self.sheet_triple_header(['Physical Attributes', 'Social Attributes', 'Mental Attributes'],
                                                width=width))
        col_widths = self.calculate_widths(width)
        physical = '\n'.join([stat.sheet_format(width=col_widths[0]-2, colors=colors) for stat in self.physical])
        social = '\n'.join([stat.sheet_format(width=col_widths[1]-1, colors=colors) for stat in self.social])
        mental = '\n'.join([stat.sheet_format(width=col_widths[2]-1, colors=colors) for stat in self.mental])
        section.append(self.sheet_columns([physical, social, mental], width=width))
        return '\n'.join(unicode(line) for line in section)


class Skills(StatSection):
    name = 'Skills'
    list_order = 15
    kind = 'skill'

    def load(self):
        self.choices = self.handler.stats_type[self.kind]

    def sheet_render(self, width=78):
        colors = self.sheet_colors
        skills = [stat for stat in self.choices if stat.display()]
        if not skills:
            return
        section = list()
        section.append(self.sheet_header(self.name, width=width))
        skill_display = [stat.sheet_format(width=24, colors=colors) for stat in skills]
        skill_table = tabular_table(skill_display, field_width=24, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)


class Specialties(StatSection):
    name = 'Specialties'
    section_type = 'Specialty'
    list_order = 16
    specialized = tuple()
    kind = 'specialty'

    def load(self):
        self.choices = [stat for stat in self.handler.stats_dict.values() if 'special' in stat.features]
        self.specialized = [stat for stat in self.handler.stats_dict.values() if stat.specialties.count() > 0]

    def sheet_render(self, width=78):
        colors = self.sheet_colors
        specialized = self.specialized
        if not specialized:
            return
        section = list()
        skill_display = list()
        section.append(self.sheet_header(self.name, width=width))
        for stat in specialized:
            skill_display += stat.sheet_specialties(colors=colors)
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)


class Favored(StatSection):
    base_name = 'Favored'
    section_type = 'Favored Stat'
    sheet_display = False
    existing = tuple()
    kind = 'favored'

    def load(self):
        self.choices = [stat for stat in self.handler.stats_dict.values() if 'favor' in stat.features]
        self.existing = [stat for stat in self.handler.stats_dict.values() if stat.is_favored]

    def all(self):
        return self.existing


class MeritSection(SheetSection):
    name = 'DefaultMerit'
    list_order = 20
    existing = tuple()
    kind = 'merit'

    def load(self):
        self.existing = sorted([merit for merit in self.owner.storyteller.merits.all() if merit.kind.key == self.kind],
                               key=lambda mer: str(mer))

    def find_merit(self, category=None, context=None):
        pass

    def add(self, category=None, context=None, rating=None):
        if category is None:
            raise ValueError("No Merit entered to set!")
        category = dramatic_capitalize(category)
        if rating is None:
            rating = 0
        if context:
            context = dramatic_capitalize(context)
            if len([merit for merit in self.existing if merit.key == category and merit.context == context]):
                raise ValueError("Cannot add new %s. Duplicate detected." % self.kind)
        elif len([merit for merit in self.existing if merit.key == category]):
            raise ValueError("Cannot add new %s. Duplicate detected." % self.kind)

        game = self.owner.storyteller.game
        merit_kind, created = game.merits.get_or_create(key=self.kind)
        new_merit, created2 = merit_kind.characters.get_or_create(character=self.owner.storyteller,
                                                                  key=category, context=context, rating=rating)
        self.load()
        return new_merit

    def sheet_render(self, width=78):
        if not self.existing:
            return
        colors = self.sheet_colors
        section = list()
        merit_section = list()
        section.append(self.sheet_header(self.name, width=width))
        short_list = [merit for merit in self.existing if len(str(merit)) <= 30]
        long_list = [merit for merit in self.existing if len(str(merit)) > 30]
        short_format = [merit.sheet_format(colors=colors, width=36) for merit in short_list]
        long_format = [merit.sheet_format(width=width-4, colors=colors) for merit in long_list]
        if short_list:
            merit_section.append(tabular_table(short_format, field_width=36, line_length=width-4))
        if long_list:
            merit_section.append('\n'.join(long_format))
        section.append(self.sheet_border('\n'.join(merit_section), width=width))
        return '\n'.join(unicode(line) for line in section)


class AdvantageStatSection(SheetSection):
    name = 'DefaultAdvStat'
    list_order = 30
    kind = 'Unset'
    existing = tuple()

    def load(self):
        self.existing = [power for power in self.owner.storyteller.powers.all() if power.power.kind.key == self.kind]

    def sheet_render(self, width=78):
        powers = self.existing
        if not powers:
            return
        section = list()
        colors = self.sheet_colors
        section.append(self.sheet_header(self.name, width=width))
        skill_display = [power.sheet_format(width=23, colors=colors, mode='stat') for power in powers]
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)

    def all(self):
        return self.existing


class AdvantageWordSection(AdvantageStatSection):
    name = 'DefaultAdvPower'
    list_order = 50

    def sheet_render(self, width=78):
        powers = self.existing
        if not powers:
            return
        section = list()
        colors = self.sheet_colors
        section.append(self.sheet_header(self.name, width=width))
        skill_display = [power.sheet_format(width=23, colors=colors, mode='word') for power in powers]
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)


class TemplateSection(SheetSection):
    name = 'Template'
    list_order = 0
    kind = 'template'

    def sheet_render(self, width=78):
        servername = unicode(settings.SERVERNAME)
        colors = self.sheet_colors
        line1 = '  {%s.%s.{n' % (colors['border'], '-' * (width-6))
        line2 = ' {%s/{n%s{n{%s\\{n' % (colors['border'], servername.center(width-4), colors['border'])
        line3 = self.sheet_header(width=width)
        name = self.owner.key
        power = self.handler.stats_dict['essence']
        powername = 'Essence'
        column_1 = ['Name']
        column_1 += self.owner.storyteller.sheet_column_1
        column_2 = [powername]
        column_2 += self.owner.storyteller.sheet_column_2
        column_1_len = max([len(entry) for entry in column_1])
        column_2_len = max([len(entry) for entry in column_2])
        column_1_prep = list()
        column_2_prep = list()
        for entry in column_1:
            if entry == 'Name':
                display = '%s: %s' % ('Name'.rjust(column_1_len), name)
            else:
                display = '%s: %s' % (entry.rjust(column_1_len), self.owner.storyteller.get(entry))
            column_1_prep.append(display)
        for entry in column_2:
            if entry == powername:
                display = '%s: %s' % (powername.rjust(column_2_len), int(power))
            else:
                display = '%s: %s' % (entry.rjust(column_2_len), self.owner.storyteller.get(entry))
            column_2_prep.append(display)
        line4 = self.sheet_two_columns(['\n'.join(column_1_prep), '\n'.join(column_2_prep)], width=width)
        return '\n'.join(unicode(line) for line in [line1, line2, line3, line4])


class StorytellerHandler(object):
    stats_dict = dict()
    stats_values = dict()
    stats_type = dict()
    owner = None
    sheet_sections = tuple()
    render_sections = tuple()
    sheet_dict = dict()

    def __repr__(self):
        return '<StorytellerHandler for %s>' % self.owner.key

    def __init__(self, owner):
        """
        'Owner' must be an instance of StorytellerCharacter.
        """
        self.owner = owner
        self.load()


    def load(self):

        stat_types = list()
        owner = self.owner
        for stat in owner.storyteller.stats.all():
            self.stats_dict[stat.stat.key] = stat
            self.stats_values[stat.stat.key] = stat.rating
            stat_types.append(stat.kind)

        stat_types = set(stat_types)
        for kind in stat_types:
            self.stats_type[kind] = sorted([stat for stat in owner.storyteller.stats.all() if stat.kind == kind],
                                           key=lambda stat2: stat2.list_order)

        self.sheet_sections = list()
        for section in self.owner.sheet_sections:
            section_obj = section(handler=self)
            self.sheet_sections.append(section_obj)
            self.sheet_dict[section_obj.kind] = section_obj
        self.sheet_sections = sorted(self.sheet_sections, key=lambda stat: stat.list_order)
        self.render_sections = [section for section in self.sheet_sections if section.sheet_display]

    def render_sheet(self, viewer=None, width=None):
        if not width and viewer:
            width = viewer.screen_width
        elif not width and not viewer:
            width = 78
        sheet = list()
        for section in self.render_sections:
            sheet.append(section.sheet_render(width=width))
        return '\n'.join(line for line in sheet if line)
