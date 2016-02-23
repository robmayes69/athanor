from __future__ import unicode_literals

import math
from django.conf import settings
from evennia.utils.evtable import EvTable
from evennia.utils.ansi import ANSIString
from commands.library import partial_match, sanitize_string, tabular_table
from evennia.utils.utils import make_iter


class SheetSection(object):

    name = 'DefaultSection'
    list_order = 0
    sheet_display = True
    use_editchar = True
    editchar_options = list()
    editchar_default = None

    def __init__(self, owner):
        self.owner = owner
        self.load()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def load(self):
        pass

    def sheet_render(self, width=78):
        return None

    @property
    def sheet_colors(self):
        color_dict = dict()
        color_dict.update(self.owner.ndb.template.template.base_sheet_colors)
        color_dict.update(self.owner.ndb.template.template.extra_sheet_colors)
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
            raise ValueError("No %s entered to set!" % self.section_type)
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
            except ValueError as err:
                error_list.append(str(err))
                continue
        if succeed_list:
            self.save()
        return succeed_list, error_list

    def set(self, choice=None, value=None, no_save=False):
        if not choice:
            raise ValueError("No %s entered to set!" % self.section_type)
        if not value:
            raise ValueError("No value entered to set '%s' to!" % choice)
        find_stat = partial_match(choice, self.choices)
        if not find_stat:
            raise ValueError("Could not find %s '%s'." % (self.section_type, choice))
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
            raise ValueError("Nothing entered to favor!")
        save = False
        stats_ok = list()
        for stat in make_iter(stat_list):
            find_stat = partial_match(stat, self.favorable)
            if not find_stat:
                continue
            stats_ok.append(find_stat)
        if not stats_ok:
            raise ValueError("No stat from the provided list could be found.")
        for stat in stats_ok:
            stat.current_favored = True
        self.save()
        return stats_ok


    def editchar_unfavor(self, stat_list=None, caller=None):
        if not stat_list:
            raise ValueError("Nothing entered to unfavor!")
        save = False
        stats_ok = list()
        for stat in make_iter(stat_list):
            find_stat = partial_match(stat, self.favored)
            if not find_stat:
                continue
            stats_ok.append(find_stat)
        if not stats_ok:
            raise ValueError("No stat from the provided list could be found.")
        for stat in stats_ok:
            stat.current_favored = False
        self.save()
        return stats_ok

    def editchar_supernal(self, stat_list=None, caller=None):
        if not stat_list:
            raise ValueError("Nothing entered to supernal!")
        save = False
        stats_ok = list()
        for stat in make_iter(stat_list):
            find_stat = partial_match(stat, self.supernable)
            if not find_stat:
                continue
            stats_ok.append(find_stat)
        if not stats_ok:
            raise ValueError("No stat from the provided list could be found.")
        for stat in stats_ok:
            stat.current_supernal = True
        self.save()
        return stats_ok

    def editchar_unsupernal(self, stat_list=None, caller=None):
        if not stat_list:
            raise ValueError("Nothing entered to unsupernal!")
        save = False
        stats_ok = list()
        for stat in make_iter(stat_list):
            find_stat = partial_match(stat, self.supernal)
            if not find_stat:
                continue
            stats_ok.append(find_stat)
        if not stats_ok:
            raise ValueError("No stat from the provided list could be found.")
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
            raise ValueError("No stat entered to specialize.")
        if not name:
            raise ValueError("No specialty name entered.")
        if not value:
            raise ValueError("Nothing entered to set it to.")
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("Specialties must be positive integers.")
        if new_value < 0:
            raise ValueError("Specialties must be positive integers.")
        found_stat = partial_match(stat, self.choices)
        if not found_stat:
            raise ValueError("Stat '%s' not found." % stat)
        new_name = sanitize_string(name, strip_ansi=True, strip_indents=True, strip_newlines=True, strip_mxp=True)
        if '-' in new_name or '+' in new_name:
            raise ValueError("Specialties cannot contain the - or + characters.")
        if new_value == 0 and new_name.lower() in found_stat.specialties:
            found_stat.specialties.pop(new_name.lower())
        elif new_value == 0:
            raise ValueError("Specialties cannot be zero dots!")
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
            raise ValueError("Stat to tag is empty!")
        found_stat = partial_match(stat, self.choices)
        if not found_stat:
            raise ValueError("Stat not found.")
        found_stat.current_favored = True
        if not no_save:
            self.save()
        return found_stat

    def remove(self, stat=None, no_save=False):
        if not stat:
            raise ValueError("Stat to tag is empty!")
        found_stat = partial_match(stat, self.existing)
        if not found_stat:
            raise ValueError("'%s' is not a %s" % (stat, self.section_type))
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
    custom_type = None
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
    custom_type = None

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
    custom_type = None

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

    def __repr__(self):
        return '<StorytellerHandler>'

    def __init__(self, owner):
        self.owner = owner
        self.load()

    def load(self):
        self.load_template()
        self.load_stats()
        self.load_pools()

    def load_template(self):
        owner = self.owner
        valid_templates = owner.storyteller_templates
        db_name = owner.storyteller_storage['template']
        save_data = owner.attributes.get(db_name, dict())
        key = save_data.get('key', 'mortal')
        info_dict = save_data.get('info', dict())
        if key not in valid_templates.keys():
            key = 'mortal'
            info_dict = dict()
        self.template = Template(key=key, init_data=valid_templates[key], info_dict=info_dict)
        owner.ndb.template = self.template
        self.save_template()

    def save_template(self):
        owner = self.owner
        db_name = owner.storyteller_storage['template']
        owner.attributes.add(db_name, self.template.export())

    def load_stats(self):
        owner = self.owner
        db_name = owner.storyteller_storage['stats']
        save_data = owner.attributes.get(db_name, dict())
        init_stats = list()
        for key in owner.storyteller_stats.keys():
            stat = Stat(key=key, init_data=owner.storyteller_stats[key], save_data=save_data.get(key, dict()))
            init_stats.append(stat)
        self.stats = sorted(init_stats, key=lambda stat: stat.list_order)
        self.stats_dict = dict()
        for stat in init_stats:
            self.stats_dict[stat.key] = int(stat)
        owner.ndb.stats_dict = self.stats_dict
        stat_types = list(set([stat.type for stat in self.stats]))
        self.stats_type = dict()
        for type in stat_types:
            self.stats_type[type] = tuple(sorted([stat for stat in self.stats if stat.type == type],
                                                 key=lambda stat2: stat2.list_order))
        owner.ndb.stats_type = self.stats_type
        self.save_stats()

    def save_stats(self):
        owner = self.owner
        db_name = owner.storyteller_storage['stats']
        export_data = {stat.key: stat.export() for stat in self.stats}
        owner.attributes.add(db_name, export_data)

    def change_template(self):
        pass

    def load_pools(self):
        owner = self.owner
        db_name = owner.storyteller_storage['pools']
        save_data = owner.attributes.get(db_name, dict())
        valid_pools = owner.storyteller_pools
        pools = list()
        for key in owner.ndb.template.pools.keys():
            pool = Pool(key=key, init_data=valid_pools.get(key, dict()), save_data=save_data.get(key, None))
            pools.append(pool)
        self.pools = sorted(pools, key=lambda order: order.list_order)
        owner.ndb.pools = self.pools
        self.save_pools()

    def save_pools(self):
        owner = self.owner
        db_name = owner.storyteller_storage['pools']
        export_data = dict()
        for pool in self.pools:
            export_data[pool.key] = pool.used
        owner.attributes.add(db_name, export_data)

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


class Template(object):

    pools = dict()
    info = dict()
    info_fields = dict()
    info_choices = dict()
    info_defaults = dict()
    charm_type = ''
    list_order = 0
    base_sheet_colors = {'title': 'n', 'border': 'n', 'textfield': 'n', 'texthead': 'n', 'colon': 'n',
                         'section_name': 'n', '3_column_name': 'n', 'advantage_name': 'n', 'advantage_border': 'n',
                         'slash': 'n', 'statdot': 'n', 'statfill': 'n', 'statname': 'n', 'damagename': 'n',
                         'damagetotal': 'n', 'damagetotalnum': 'n'}
    extra_sheet_colors = dict()
    sheet_column_1 = list()
    sheet_column_2 = list()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __nonzero__(self):
        return True

    def __init__(self, key=None, init_data=None, info_dict=None):
        if not info_dict:
            info_dict = dict()
        self.key = key
        self.name = init_data['name']
        keys = init_data.keys()
        for category in ('info_defaults', 'info_choices', 'pools', 'charm_type', 'list_order', 'extra_sheet_colors',
                         'sheet_column_1', 'sheet_column_2'):
            if category in keys:
                setattr(self, category, init_data[category])

        self.info.update(self.info_defaults)

        for key in self.info_fields.keys():
            self.info[key] = info_dict.get(key)

    def export(self):
        return {'key': self.key, 'info': self.info}


    def get(self, field=None):
        if not field:
            return
        info_dict = dict(self.info_defaults)
        info_dict.update(self.info)
        try:
            response = info_dict[field]
        except KeyError:
            return None
        return response

    def set(self, field=None, value=None):
        if not field:
            raise KeyError("No field entered to set!")
        found_field = partial_match(field, self.info_fields)
        if not found_field:
            raise KeyError("Field '%s' not found." % field)
        if not value:
            try:
                self.info_fields.pop(found_field)
            except KeyError:
                return True
        if found_field in self.info_choices:
            choices = self.info_choices[found_field]
            find_value = partial_match(value, choices)
            if not find_value:
                raise KeyError("'%s' is not a valid entry for %s. Choices are: %s" % (value, found_field,
                                                                                          ', '.join(choices)))
            self.info[found_field] = find_value
        else:
            self.info[found_field] = sanitize_string(value)


class ProtoStat(object):
    """
    This provides logic for the other Stat classes. It is not used directly.
    """

    name = 'Unset'
    value = 0
    specialties_storage = dict()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<%s: %s - (%s)>' % (type(self).__name__, self.name, self.rating)

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    def __int__(self):
        return self.rating

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.__name

    def __hash__(self):
        return hash(self.name) ^ hash(type(self).__name__)

    def __add__(self, other):
        return int(self) + int(other)

    def __radd__(self, other):
        return int(self) + int(other)

    @property
    def rating(self):
        return self.value

    @rating.setter
    def rating(self, value):
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("'%s' must be set to a positive integer." % self)
        if not new_value >= 0:
            raise ValueError("'%s' must be set to a positive integer." % self)
        self.value = new_value

    def set_specialty(self, name, value):
        name = name.lower()
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("Specialties must be set to whole numbers.")
        if not new_value >= 0:
            raise ValueError("Specialties cannot be negative numbers.")
        if new_value == 0 and name in self.specialties_storage.keys():
            self.specialties_storage.pop(name, None)
            return
        self.specialties_storage[name] = new_value


class Stat(ProtoStat):
    """
    This class is used for all of the 'default' stats provided by a Storyteller game. Attributes, Skills, etc.
    """

    def __init__(self, key=None, init_data=None, save_data=None):
        if not save_data:
            save_data = dict()
        self.key = key
        self.name = init_data.get('name')
        self.tags = init_data.get('tags', tuple())
        self.type = init_data.get('type', '')
        self.__favored = save_data.get('favored', False)
        self.__supernal = save_data.get('supernal', False)
        self.__epic = save_data.get('epic', False)
        self.list_order = init_data.get('list_order', 0)
        self.category = init_data.get('category', '')
        self.sub_category = init_data.get('sub_category', '')
        self.value = save_data.get('rating', init_data.get('start_value', 0))


    def __hash__(self):
        return hash(self.key)

    @property
    def favored(self):
        return self.__favored

    @favored.setter
    def favored(self, value):
        if 'no_favor' in self.tags:
            raise ValueError("'%s' cannot be set Favored." % self)
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("'%s' Favored must be set to 0 or 1." % self)
        if new_value not in [0, 1]:
            raise ValueError("'%s' Favored must be set to 0 or 1." % self)
        self.__favored = bool(new_value)

    @property
    def supernal(self):
        return self.__supernal

    @supernal.setter
    def supernal(self, value):
        if 'no_supernal' in self.tags:
            raise ValueError("'%s' cannot be set Supernal." % self)
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("'%s' Supernal must be set to 0 or 1." % self)
        if new_value not in [0, 1]:
            raise ValueError("'%s' Supernal must be set to 0 or 1." % self)
        self.__supernal = bool(new_value)

    @property
    def epic(self):
        return self.__supernal

    @epic.setter
    def epic(self, value):
        if 'no_epic' in self.tags:
            raise ValueError("'%s' cannot be set Epic." % self)
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("'%s' Epic must be set to 0 or 1." % self)
        if new_value not in [0, 1]:
            raise ValueError("'%s' Epic must be set to 0 or 1." % self)
        self.__epic = bool(new_value)

    def display(self):
        return self.supernal or self.favored or self.epic or int(self)

    def export(self):
        return {'rating': self.value, 'favored': self.__favored, 'supernal': self.__supernal, 'epic': self.__epic}

"""
    def sheet_format(self, width=23, no_favored=False, fill_char='.',
                     colors={'statname': 'n', 'statfill': 'n', 'statdot': 'n'}):
        display_name = ANSIString('{%s%s{n' % (colors['statname'], self.full_name))
        if self.current_supernal:
            fav_dot = ANSIString('{r*{n')
        elif self.current_favored:
            fav_dot = ANSIString('{r+{n')
        else:
            fav_dot = ANSIString(' ')
        if not no_favored:
            display_name = fav_dot + display_name
        if self.current_value > width - len(display_name) - 1:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], self.current_value))
        else:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], '*' * self.current_value))
        fill_length = width - len(display_name) - len(dot_display)
        fill = ANSIString('{%s%s{n' % (colors['statfill'], fill_char * fill_length))
        return display_name + fill + dot_display

    def sheet_specialties(self, width=35, fill_char='.', colors={'statname': 'n', 'statfill': 'n', 'statdot': 'n'}):
        specialty_list = list()
        for specialty, value in self.specialties.items():
            display_name = ANSIString('{%s%s/%s{n' % (colors['statname'], self.full_name,
                                                      dramatic_capitalize(specialty)))
            if value > width - len(display_name) - 1:
                dot_display = ANSIString('{%s%s{n' % (colors['statdot'], self.current_value))
            else:
                dot_display = ANSIString('{%s%s{n' % (colors['statdot'], '*' * self.current_value))
            fill_length = width - len(display_name) - len(dot_display)
            fill = ANSIString('{%s%s{n' % (colors['statfill'], fill_char * fill_length))
            specialty_display = display_name + fill + dot_display
            specialty_list.append(specialty_display)
        return specialty_list
"""


class CustomStat(ProtoStat):
    """
    This class is used for all of the custom stats like Crafts or Styles..
    """

    tags = list()
    type = 'Stat'
    category = ''
    sub_category = ''

    def export(self):
        return (self.name, (self.value, self.type, self.category, self.sub_category, self.tags))



class Pool(object):

    key = ''
    name = 'Pool'
    category = 'Pool'
    unit = ''
    list_order = 0
    tags = tuple()
    refresh = ''
    __commits = dict()
    owner = None
    __used = 0
    __func = None

    def __repr__(self):
        return '<%s: %s/%s>' % (self.name, self.available, self.max)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __int__(self):
        return self.available

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __init__(self, key=None, init_data=None, save_data=None):
        self.key = key
        for category in ('name', 'unit', 'tags', 'refresh', 'category'):
            if category in init_data.keys():
                setattr(self, category, init_data[category])
        self.__used = save_data or 0
            

    @property
    def used(self):
        return self.__used

    @property
    def max(self):
        return self.__func(self.owner)

    @property
    def available(self):
        return self.max - self.total_commit - self.__used

    @property
    def total_commit(self):
        return sum(self.__commits.values())

    def commit(self, reason=None, amount=None):
        if not reason:
            raise ValueError("Reason is empty!")
        try:
            value = int(amount)
        except ValueError:
            raise ValueError("Amount must be an integer.")
        if value < 1:
            raise ValueError("Commitments must be positive integers.")
        if value > self.available:
            raise ValueError("Cannot commit more than you have!")
        if reason.lower() in [key.lower() for key in self.__commits.keys()]:
            raise ValueError("Commitments must be unique.")
        self.__commits[reason] = value
        return True

    def uncommit(self, reason=None):
        if not reason:
            raise ValueError("Reason is empty!")
        find_reason = partial_match(reason, self.commitments.keys())
        if not find_reason:
            raise ValueError("Commitment not found.")
        self.commitments.pop(find_reason)
        return True

    def fill(self, amount=None):
        try:
            value = int(amount)
        except ValueError:
            raise ValueError("Values must be integers.")
        if not value > 0:
            raise ValueError("Values must be positive.")
        if (self.current_value + value) > self.max:
            raise ValueError("That would exceed the pool's current capacity.")
        self.current_value += value
        return True

    def drain(self, amount=None):
        try:
            value = int(amount)
        except ValueError:
            raise ValueError("Values must be integers.")
        if not value > 0:
            raise ValueError("Values must be positive.")
        if value > self.current_value:
            raise ValueError("There aren't that many %s to spend!" % self.component_plural)
        self.current_value -= value
        return True

    def refresh_pool(self):
        self.__used = 0

    def sheet_format(self, rjust=None, zfill=2):
        val_string = '%s/%s' % (str(self.current_value).zfill(zfill), str(self.max).zfill(zfill))
        display_name = self.name
        if rjust:
            return '%s: %s' % (self.name.rjust(rjust), val_string)
        else:
            return '%s: %s' % (self.name, val_string)