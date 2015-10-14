import math
from django.conf import settings
from commands.library import AthanorError, partial_match, tabular_table
from evennia.utils.evtable import EvTable
from evennia.utils.ansi import ANSIString

class Template(object):

    game_category = 'Storyteller'
    base_name = 'Mortal'
    default_pools = []
    sub_class_list = []
    sub_class = None
    sub_class_name = None
    power_stat = None
    base_sheet_colors = {'title': 'n', 'border': 'n', 'textfield': 'n', 'texthead': 'n', 'colon': 'n',
                         'section_name': 'n', '3_column_name': 'n', 'advantage_name': 'n', 'advantage_border': 'n',
                         'slash': 'n', 'statdot': 'n', 'statfill': 'n', 'statname': 'n', 'damagename': 'n',
                         'danagetotal': 'n', 'damagetotalnum': 'n'}
    extra_sheet_colors = dict()

    def __str__(self):
        return self.base_name

    def __unicode__(self):
        return unicode(self.base_name)

    def __nonzero__(self):
        return True

    @property
    def sheet_colors(self):
        color_dict = dict()
        color_dict.update(self.base_sheet_colors)
        color_dict.update(self.extra_sheet_colors)
        return color_dict

    def render_sheet(self, owner, viewer=None, width=None):
        if not width and viewer:
            width = viewer.screen_width
        elif not width and not viewer:
            width = 78
        sheet = list()
        sheet += self.sheet_game(owner, width)
        sheet += self.sheet_attributes(owner, width)
        sheet += self.sheet_skills(owner, width)
        sheet += self.sheet_merits(owner, width)
        sheet += self.sheet_advantages(owner, width)
        sheet += self.sheet_pools(owner, width)
        return '\n'.join(unicode(line) for line in sheet if line)

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

    def sheet_triple_header(self, display_text = ['', '', ''], width=78):
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

    def sheet_game(self, owner, width=78):
        colors = self.sheet_colors
        line1 = '  {%s.%s.{n' % (colors['border'], '-' * (width-6))
        line2_start = ' {%s/{n' % colors['border']
        line2_end = ' {%s\\{n' % colors['border']
        line2 = line2_start + '%s' % settings.SERVERNAME.center(width-5, ' ') + line2_end
        return [line1, line2]

    def sheet_attributes(self, owner, width=78):
        section = list()
        section.append(self.sheet_triple_header(['Physical Attributes', 'Social Attributes', 'Mental Attributes'],
                                                width=width))
        col_widths = self.calculate_widths(width)
        physical = '\n'.join([stat.sheet_format(width=col_widths[0]-2) for stat in owner.stats.attributes_physical])
        social = '\n'.join([stat.sheet_format(width=col_widths[1]-2) for stat in owner.stats.attributes_social])
        mental = '\n'.join([stat.sheet_format(width=col_widths[2]-2) for stat in owner.stats.attributes_mental])
        section.append(self.sheet_columns([physical, social, mental], width=width))
        return section

    def sheet_skills(self, owner, width=78):
        skills = [stat for stat in owner.stats.skill_stats if stat.should_display()]
        if not skills:
            return
        section = list()
        section.append(self.sheet_header('Skills', width=width))
        skill_display = [stat.sheet_format(width=23) for stat in skills]
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return section

    def sheet_advantages(self, owner, width=78):
        pass

    def sheet_merits(self, owner, width=78):
        merits = sorted(list(owner.merits.cache_merits), key=lambda merit2: merit2.full_name)
        if not merits:
            return
        merit_types = sorted(list(set(merit.base_name for merit in merits)))
        section = list()
        for merit_type in merit_types:
            merit_section = list()
            section.append(self.sheet_header(merit_type, width=width))
            merit_list = [merit for merit in merits if merit.base_name == merit_type]
            short_list = [merit for merit in merit_list if len(merit.full_name) <= 30]
            long_list = [merit for merit in merit_list if len(merit.full_name) > 30]
            short_format = [merit.sheet_format() for merit in short_list]
            long_format = [merit.sheet_format(width=width-4) for merit in long_list]
            if short_list:
                merit_section.append(tabular_table(short_format, field_width=36, line_length=width-4))
            if long_list:
                merit_section.append('\n'.join(long_format))
            section.append(self.sheet_border('\n'.join(merit_section), width=width))
        return section

    def sheet_pools(self, owner, width=78):
        pass

    def calculate_widths(self, width=78):
        column_widths = list()
        col_calc = (width) / float(3)
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

class TemplateHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.load()
        self.save(no_load=True)

    def load(self):
        load_db = self.owner.storage_locations['template']
        load_template = self.owner.attributes.get(load_db)
        if not load_template:
            self.swap('Mortal', no_save=True)
        else:
            self.template = load_template

    def save(self, no_load=False):
        load_db = self.owner.storage_locations['template']
        self.owner.attributes.add(load_db, self.template)
        if not no_load:
            self.load()

    def swap(self, new_template=None, no_save=False):
        if not new_template:
            raise AthanorError("New Template field empty!")
        new_templates = [template() for template in self.owner.valid_templates]
        new_find = partial_match(new_template, new_templates)
        if not new_find:
            raise AthanorError("Template '%s' not found." % new_template)
        self.template = new_find
        if not no_save:
            self.save()
            self.owner.stats.load()
            self.owner.merits.load()
            self.owner.advantages.load()
            self.owner.pools.load()

    @property
    def power(self):
        return self.template.power_stat

    @property
    def pools(self):
        return self.template.default_pools

    def sheet(self, viewer=None, width=None):
        return self.template.render_sheet(self.owner, viewer, width)