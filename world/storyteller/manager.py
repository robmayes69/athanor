import math
from django.conf import settings
from evennia.utils.evtable import EvTable
from evennia.utils.ansi import ANSIString
from commands.library import AthanorError, partial_match, sanitize_string, tabular_table
from world.storyteller.merits import Merit
from world.storyteller.advantages import WordPower, StatPower
from evennia.utils.utils import make_iter

class SheetSection(object):

    base_name = 'DefaultSection'
    list_order = 0
    sheet_display = True
    use_editchar = True
    editchar_options = list()
    editchar_default = None

    def __init__(self, owner):
        self.owner = owner
        self.load()

    def __str__(self):
        return self.base_name

    def __unicode__(self):
        return unicode(self.base_name)

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

    def sheet_two_columns(self, display_text=['', ''], width=78):
        colors = self.sheet_colors
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

    section_type = 'Stat'
    editchar_default = 'set'
    editchar_options = ['set']
    favorable = list()
    supernable = list()
    favored = list()
    supernal = list()

    def editchar_set(self, extra_args=[], single_arg=None, list_arg=[], caller=None):
        if not list_arg:
            raise AthanorError("No %s entered to set!" % self.section_type)
        valid_entries = dict()
        error_list = list()
        succeed_list = list()
        for entry in list_arg:
            try:
                choice, value = entry.split('=', 1)
                choice = choice.strip().lower()
                value = value.strip()
            except ValueError:
                error_list.append("'%s' was not an accepted %s entry. Accepted Format: <Stat>=<Value>" %
                                   (entry, self.section_type))
            else:
                valid_entries[choice] = value

        for choice, value in valid_entries.items():
            find_stat = partial_match(choice, self.choices)
            if not find_stat:
                error_list.append("Could not find %s: '%s'" % (self.section_type, choice))
                continue
            try:
                find_stat.current_value = value
                succeed_list.append(find_stat)
            except AthanorError as err:
                error_list.append(str(err))
                continue
        if succeed_list:
            self.save()
        return succeed_list, error_list

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

    def editchar_favor(self, stat_list=None, caller=None):
        if not stat_list:
            raise AthanorError("Nothing entered to favor!")
        save = False
        stats_ok = list()
        for stat in make_iter(stat_list):
            find_stat = partial_match(stat, self.favorable)
            if not find_stat:
                continue
            stats_ok.append(find_stat)
        if not stats_ok:
            raise AthanorError("No stat from the provided list could be found.")
        for stat in stats_ok:
            stat.current_favored = True
        self.save()
        return stats_ok


    def editchar_unfavor(self, stat_list=None, caller=None):
        if not stat_list:
            raise AthanorError("Nothing entered to unfavor!")
        save = False
        stats_ok = list()
        for stat in make_iter(stat_list):
            find_stat = partial_match(stat, self.favored)
            if not find_stat:
                continue
            stats_ok.append(find_stat)
        if not stats_ok:
            raise AthanorError("No stat from the provided list could be found.")
        for stat in stats_ok:
            stat.current_favored = False
        self.save()
        return stats_ok

    def editchar_supernal(self, stat_list=None, caller=None):
        if not stat_list:
            raise AthanorError("Nothing entered to supernal!")
        save = False
        stats_ok = list()
        for stat in make_iter(stat_list):
            find_stat = partial_match(stat, self.supernable)
            if not find_stat:
                continue
            stats_ok.append(find_stat)
        if not stats_ok:
            raise AthanorError("No stat from the provided list could be found.")
        for stat in stats_ok:
            stat.current_supernal = True
        self.save()
        return stats_ok

    def editchar_unsupernal(self, stat_list=None, caller=None):
        if not stat_list:
            raise AthanorError("Nothing entered to unsupernal!")
        save = False
        stats_ok = list()
        for stat in make_iter(stat_list):
            find_stat = partial_match(stat, self.supernal)
            if not find_stat:
                continue
            stats_ok.append(find_stat)
        if not stats_ok:
            raise AthanorError("No stat from the provided list could be found.")
        for stat in stats_ok:
            stat.current_supernal = False
        self.save()
        return stats_ok

class Attributes(StatSection):
    base_name = 'Attributes'
    section_type = 'Attribute'
    list_order = 10

    def load(self):
        self.choices = self.owner.stats.category('Attribute')
        self.favorable = [stat for stat in self.choices if stat.can_favor]
        self.favored = [stat for stat in self.choices if stat.current_favored]
        self.supernal = [stat for stat in self.choices if stat.current_supernal]
        for stat_type in ['Physical', 'Social', 'Mental']:
            setattr(self, stat_type.lower(), [stat for stat in self.choices if stat.sub_category == stat_type])

    def sheet_render(self, width=78):
        colors = self.sheet_colors
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
    base_name = 'Skills'
    section_type = 'Skill'
    list_order = 15

    def load(self):
        self.choices = self.owner.stats.category('Skill')

    def sheet_render(self, width=78):
        colors = self.sheet_colors
        skills = [stat for stat in self.choices if stat.should_display()]
        if not skills:
            return
        section = list()
        section.append(self.sheet_header(self.base_name, width=width))
        skill_display = [stat.sheet_format(width=23, colors=colors) for stat in skills]
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)


class Specialties(StatSection):
    base_name = 'Specialties'
    section_type = 'Specialty'
    list_order = 16
    editchar_default = 'set'

    def load(self):
        self.choices = [stat for stat in self.owner.stats.all() if stat.can_specialize]
        self.specialized = [stat for stat in self.owner.stats.all() if stat.specialties]

    def editchar_set(self, stat=None, name=None, value=None):
        if not stat:
            raise AthanorError("No stat entered to specialize.")
        if not name:
            raise AthanorError("No specialty name entered.")
        if not value:
            raise AthanorError("Nothing entered to set it to.")
        try:
            new_value = int(value)
        except ValueError:
            raise AthanorError("Specialties must be positive integers.")
        if new_value < 0:
            raise AthanorError("Specialties must be positive integers.")
        found_stat = partial_match(stat, self.choices)
        if not found_stat:
            raise AthanorError("Stat '%s' not found." % stat)
        new_name = sanitize_string(name, strip_ansi=True, strip_indents=True, strip_newlines=True, strip_mxp=True)
        if '-' in new_name or '+' in new_name:
            raise AthanorError("Specialties cannot contain the - or + characters.")
        if new_value == 0 and new_name.lower() in found_stat.specialties:
            found_stat.specialties.pop(new_name.lower())
        elif new_value == 0:
            raise AthanorError("Specialties cannot be zero dots!")
        else:
            found_stat.specialties[new_name.lower()] = new_value
        self.save()
        return True

    def sheet_render(self, width=78):
        colors = self.sheet_colors
        specialized = self.specialized
        if not specialized:
            return
        section = list()
        skill_display = list()
        section.append(self.sheet_header(self.base_name, width=width))
        for stat in specialized:
            skill_display += stat.sheet_specialties(colors=colors)
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)


class Favored(StatSection):
    base_name = 'Favored'
    section_type = 'Favored Stat'
    sheet_display = False

    def load(self):
        self.choices = [stat for stat in self.owner.stats.all() if stat.can_favor]
        self.existing = [stat for stat in self.owner.stats.all() if stat.current_favored]

    def add(self, stat=None, no_save=False):
        if not stat:
            raise AthanorError("Stat to tag is empty!")
        found_stat = partial_match(stat, self.choices)
        if not found_stat:
            raise AthanorError("Stat not found.")
        found_stat.current_favored = True
        if not no_save:
            self.save()
        return found_stat

    def remove(self, stat=None, no_save=False):
        if not stat:
            raise AthanorError("Stat to tag is empty!")
        found_stat = partial_match(stat, self.existing)
        if not found_stat:
            raise AthanorError("'%s' is not a %s" % (stat, self.section_type))
        found_stat.current_favored = False
        if not no_save:
            self.save()
        return found_stat

    def all(self):
        return self.existing

    def save(self):
        super(Favored, self).save()
        self.load()

class MeritSection(SheetSection):
    base_name = 'DefaultMerit'
    list_order = 20
    custom_type = Merit
    sheet_name = 'Default Merits'

    def load(self):
        self.existing = [merit for merit in self.owner.merits.all() if isinstance(merit, self.custom_type)]

    def sheet_render(self, width=78):
        if not self.existing:
            return
        colors = self.sheet_colors
        section = list()
        merit_section = list()
        section.append(self.sheet_header(self.sheet_name, width=width))
        short_list = [merit for merit in self.existing if len(merit.full_name) <= 30]
        long_list = [merit for merit in self.existing if len(merit.full_name) > 30]
        short_format = [merit.sheet_format(colors=colors) for merit in short_list]
        long_format = [merit.sheet_format(width=width-4, colors=colors) for merit in long_list]
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
        colors = self.sheet_colors
        section.append(self.sheet_header(self.base_name, width=width))
        skill_display = [power.sheet_format(width=23, colors=colors) for power in powers]
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
        colors = self.sheet_colors
        section.append(self.sheet_header(self.base_name, width=width))
        skill_display = [power.sheet_format(width=23, colors=colors) for power in powers]
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)

    def all(self):
        return self.existing

class FirstSection(SheetSection):
    use_editchar = False
    list_order = 0

    def sheet_render(self, width=78):
        servername = settings.SERVERNAME
        colors = self.sheet_colors
        line1 = '  {%s.%s.{n' % (colors['border'], '-' * (width-6))
        line2 = ' {%s/{n%s{n{%s\\{n' % (colors['border'], servername.center(width-4, ' '), colors['border'])
        line3 = self.sheet_header(width=width)
        name = self.owner.key
        power = self.owner.stats.get('Power')
        powername = str(power)
        column_1 = ['Name']
        column_1 += self.owner.template.template.sheet_column_1
        column_2 = [powername]
        column_2 += self.owner.template.template.sheet_column_2
        column_1_len = max([len(entry) for entry in column_1])
        column_2_len = max([len(entry) for entry in column_2])
        column_1_prep = list()
        column_2_prep = list()
        for entry in column_1:
            if entry == 'Name':
                display = '%s: %s' % ('Name'.rjust(column_1_len), name)
            else:
                display = '%s: %s' % (entry.rjust(column_1_len), self.owner.template.template.get(entry))
            column_1_prep.append(display)
        for entry in column_2:
            if entry == powername:
                display = '%s: %s' % (powername.rjust(column_2_len), int(power))
            else:
                display = '%s: %s' % (entry.rjust(column_2_len), self.owner.template.template.get(entry))
            column_2_prep.append(display)
        line4 = self.sheet_two_columns(['\n'.join(column_1_prep), '\n'.join(column_2_prep)], width=width)
        return '\n'.join(unicode(line) for line in [line1, line2, line3, line4])

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
