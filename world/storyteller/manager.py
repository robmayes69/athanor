import math
from evennia.utils.evtable import EvTable
from evennia.utils.ansi import ANSIString
from commands.library import AthanorError, partial_match, sanitize_string, tabular_table
from world.storyteller.merits import Merit
from world.storyteller.advantages import WordPower, StatPower

class SheetSection(object):

    base_name = 'DefaultSection'
    list_order = 0
    sheet_display = True
    use_editchar = True

    def __init__(self, owner):
        self.owner = owner
        self.load()

    def load(self):
        pass

    def sheet_render(self, width=78):
        return None

    @property
    def sheet_colors(self):
        color_dict = dict()
        color_dict.update(self.owner.template.template.base_sheet_colors)
        color_dict.update(self.owner.template.template.extra_sheet_colors)
        return color_dict

    def sheet_header(self, center_text=None, width=78):
        colors = self.sheet_colors
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

    def sheet_triple_header(self, display_text=['', '', ''], width=78):
        colors = self.sheet_colors
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
        colors = self.sheet_colors
        ev_table = EvTable(border='cols', pad_width=0, valign='t',
                           border_left_char=ANSIString('{%s|{n' % colors['border']),
                           border_right_char=ANSIString('{%s|{n' % colors['border']), header=False)
        ev_table.add_row(display_text, width=width)
        return ev_table

    def sheet_columns(self, display_text=['', '', ''], width=78):
        colors = self.sheet_colors
        ev_table = EvTable(border='cols', pad_width=0, valign='t',
                           border_left_char=ANSIString('{%s|{n' % colors['border']),
                           border_right_char=ANSIString('{%s|{n' % colors['border']), header=False)
        ev_table.add_row(display_text[0], display_text[1], display_text[2])

        for count, col_width in enumerate(self.calculate_widths(width=width)):
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


class StatSection(SheetSection):

    section_type = 'Stat'

    def set_multiple(self, choice_string=None):
        should_save = False
        if not choice_string:
            raise AthanorError("No %s entered to set!" % self.section_type)
        choice_string = sanitize_string(choice_string, strip_ansi=True, strip_mxp=True, strip_newlines=True,
                                        strip_indents=True)
        valid_entries = dict()
        for entry in choice_string.split(','):
            entry = entry.strip()
            try:
                choice, value = entry.split('=', 1)
                choice = choice.strip().lower()
                value = value.strip()
            except ValueError:
                raise AthanorError("'%s' was not an accepted %s entry." % (entry, self.section_type))
            valid_entries[choice] = value

        for choice, value in valid_entries.items():
            try:
                self.set(choice, value, no_save=True)
                should_save = True
            except AthanorError:
                raise
            finally:
                if should_save:
                    self.save()

    def set(self, choice=None, value=None, no_save=False):
        if not choice:
            raise AthanorError("No %s entered to set!" % self.section_type)
        if not value:
            raise AthanorError("No value entered to set '%s' to!" % choice)
        find_stat = partial_match(choice, self.choices)
        if not find_stat:
            raise AthanorError("Could not find %s '%s'." % (self.section_type, choice))
        find_stat.current_value = value
        if not no_save:
            self.save()

    def load(self):
        self.choices = self.owner.stats.all()

    def save(self):
        self.owner.stats.save()

    def all(self):
        return self.choices


class Attributes(StatSection):
    base_name = 'Attributes'
    section_type = 'Attribute'
    list_order = 10

    def load(self):
        self.choices = [stat for stat in self.owner.stats.all() if stat.main_category == 'Attribute']
        for stat_type in ['Physical', 'Social', 'Mental']:
            setattr(self, stat_type.lower(), [stat for stat in self.choices if stat.sub_category == stat_type])

    def sheet_render(self, width=78):
        section = list()
        section.append(self.sheet_triple_header(['Physical Attributes', 'Social Attributes', 'Mental Attributes'],
                                                width=width))
        col_widths = self.calculate_widths(width)
        physical = '\n'.join([stat.sheet_format(width=col_widths[0]-2) for stat in self.physical])
        social = '\n'.join([stat.sheet_format(width=col_widths[1]-1) for stat in self.social])
        mental = '\n'.join([stat.sheet_format(width=col_widths[2]-1) for stat in self.mental])
        section.append(self.sheet_columns([physical, social, mental], width=width))
        return '\n'.join(unicode(line) for line in section)


class Skills(StatSection):
    base_name = 'Skills'
    section_type = 'Skill'
    list_order = 15

    def load(self):
        self.choices = [stat for stat in self.owner.stats.all() if stat.main_category == 'Skill']

    def sheet_render(self, width=78):
        skills = [stat for stat in self.choices if stat.should_display()]
        if not skills:
            return
        section = list()
        section.append(self.sheet_header(self.base_name, width=width))
        skill_display = [stat.sheet_format(width=23) for stat in skills]
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)


class MeritSection(SheetSection):
    base_name = 'DefaultMerit'
    list_order = 20
    custom_type = Merit

    def load(self):
        self.existing = [merit for merit in self.owner.merits.all() if isinstance(merit, self.custom_type)]

    def sheet_render(self, width=78):
        if not self.existing:
            return
        section = list()
        merit_section = list()
        section.append(self.sheet_header(self.base_name, width=width))
        short_list = [merit for merit in self.existing if len(merit.full_name) <= 30]
        long_list = [merit for merit in self.existing if len(merit.full_name) > 30]
        short_format = [merit.sheet_format() for merit in short_list]
        long_format = [merit.sheet_format(width=width-4) for merit in long_list]
        if short_list:
            merit_section.append(tabular_table(short_format, field_width=36, line_length=width-4))
        if long_list:
            merit_section.append('\n'.join(long_format))
        section.append(self.sheet_border('\n'.join(merit_section), width=width))
        return '\n'.join(unicode(line) for line in section)


class AdvantageStatSection(SheetSection):
    base_name = 'DefaultAdvStat'
    list_order = 30
    custom_type = StatPower

    def load(self):
        self.existing = [power for power in self.owner.advantages.all() if isinstance(power, self.custom_type)]

    def sheet_render(self, width=78):
        powers = self.existing
        if not powers:
            return
        section = list()
        section.append(self.sheet_header(self.base_name, width=width))
        skill_display = [power.sheet_format(width=23) for power in powers]
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)

    def all(self):
        return self.existing

class AdvantageWordSection(SheetSection):
    base_name = 'DefaultAdvPower'
    list_order = 50
    custom_type = WordPower

    def load(self):
        self.existing = [power for power in self.owner.advantages.all() if isinstance(power, self.custom_type)]

    def sheet_render(self, width=78):
        powers = self.existing
        if not powers:
            return
        section = list()
        section.append(self.sheet_header(self.base_name, width=width))
        skill_display = [power.sheet_format(width=23) for power in powers]
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)

    def all(self):
        return self.existing

class StorytellerHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.load()

    def load(self):
        valid_sections = self.owner.valid_sections
        self.cache_sections = sorted([section(self.owner) for section in valid_sections], key=lambda section: section.list_order)
        self.sheet_sections = [section for section in self.cache_sections if section.sheet_display]
        self.editchar_sections = [section for section in self.cache_sections if section.use_editchar]

        for section in self.cache_sections:
            setattr(self, section.base_name.lower(), section)

    def render_sheet(self, viewer=None, width=None):
        if not width and viewer:
            width = viewer.screen_width
        elif not width and not viewer:
            width = 78
        sheet = list()
        for section in self.sheet_sections:
            sheet.append(section.sheet_render(width=width))
            print section
        print sheet
        return '\n'.join(line for line in sheet if line)
