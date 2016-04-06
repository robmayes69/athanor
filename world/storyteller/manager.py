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
        color_dict.update(self.handler.template.base_sheet_colors)
        color_dict.update(self.handler.template.extra_sheet_colors)
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
        self.choices = self.handler.stats_type[self.kind]

    def save(self):
        self.owner.storyteller.save_stats()

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
        self.existing = sorted([stat for stat in self.handler.custom if stat.kind == self.kind],
                               key=lambda stat2: stat2.key)

    def save(self):
        self.owner.storyteller.save_custom()

    def set(self, skill, rating):
        try:
            rating = int(rating)
        except ValueError:
            raise ValueError("That's not an acceptable rating!")
        find_stat = partial_match(skill, self.existing)
        if find_stat:
            if not find_stat.name.lower() == skill.lower():
                find_stat = CustomStat((self.kind, skill), self.handler)
        else:
            find_stat = CustomStat((self.kind, skill), self.handler)
        if rating > 0:
            find_stat.rating = rating
            find_stat.save()
            self.load()
        else:
            del find_stat
            self.save()

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
        self.choices = sorted(self.handler.stats_type[self.kind], key=lambda stat: stat.list_order)
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
        self.choices = [stat for stat in self.handler.stats if 'special' in stat.features]
        self.specialized = [stat for stat in self.handler.stats if len(stat._specialties) > 0]

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
        self.choices = [stat for stat in self.handler.stats if 'favor' in stat.features]
        self.existing = [stat for stat in self.handler.stats if stat._favored]

    def all(self):
        return self.existing

    def save(self):
        super(Favored, self).save()
        self.load()


class MeritSection(SheetSection):
    name = 'DefaultMerit'
    list_order = 20
    existing = tuple()
    kind = 'merit'

    def load(self):
        self.existing = sorted([merit for merit in self.handler.merits if merit.kind == self.kind],
                               key=lambda mer: mer.display_name)

    def add(self, category, context, rating=None):
        if rating is None:
            rating = 0
        new_merit = Merit(key=(self.kind, category, context), handler=self.handler)
        new_merit.rating = rating
        new_merit.save()
        self.load()
        return new_merit

    def sheet_render(self, width=78):
        if not self.existing:
            return
        colors = self.sheet_colors
        section = list()
        merit_section = list()
        section.append(self.sheet_header(self.name, width=width))
        short_list = [merit for merit in self.existing if len(merit.display_name) <= 30]
        long_list = [merit for merit in self.existing if len(merit.display_name) > 30]
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
        self.existing = [power for power in self.handler.powers if power.kind == self.kind]

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

    def save(self):
        self.handler.save_powers()
        self.handler.load_powers()

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
        column_1 += self.handler.template.sheet_column_1
        column_2 = [powername]
        column_2 += self.handler.template.sheet_column_2
        column_1_len = max([len(entry) for entry in column_1])
        column_2_len = max([len(entry) for entry in column_2])
        column_1_prep = list()
        column_2_prep = list()
        for entry in column_1:
            if entry == 'Name':
                display = '%s: %s' % ('Name'.rjust(column_1_len), name)
            else:
                display = '%s: %s' % (entry.rjust(column_1_len), self.handler.template.get(entry))
            column_1_prep.append(display)
        for entry in column_2:
            if entry == powername:
                display = '%s: %s' % (powername.rjust(column_2_len), int(power))
            else:
                display = '%s: %s' % (entry.rjust(column_2_len), self.handler.template.get(entry))
            column_2_prep.append(display)
        line4 = self.sheet_two_columns(['\n'.join(column_1_prep), '\n'.join(column_2_prep)], width=width)
        return '\n'.join(unicode(line) for line in [line1, line2, line3, line4])


class StorytellerHandler(object):
    """
    The StorytellerHandler is the core of the Storyteller data engine. This is loaded on any Character instance on
    demand via @lazy_property and uses properties from the specific typeclass of the character to determine what stats,
    powers, and etc to use.

    This per-character object is responsible for the saving, loading, and manipulating of all Storyteller data.

    See the StorytellerCharacter and derived character typeclasses for which.
    """
    stats = tuple()
    stats_dict = dict()
    stats_values = dict()
    stats_type = dict()
    owner = None
    custom = list()
    merits = list()
    pools = list()
    powers = list()
    sheet_sections = tuple()
    render_sections = tuple()
    template = None
    data_dict = dict()
    sheet_dict = dict()

    def __repr__(self):
        return '<StorytellerHandler for %s>' % self.owner.key

    def __init__(self, owner):
        """
        'Owner' must be an instance of StorytellerCharacter.
        """
        self.owner = owner
        self.load()
        self.save()

    def load(self):
        self.load_storage()
        self.load_template()
        self.load_stats()
        self.load_pools()
        self.load_custom()
        self.load_powers()
        self.load_merits()
        self.load_sheet()

    def save(self):
        self.save_template()
        self.save_stats()
        self.save_custom()
        self.save_pools()
        self.save_powers()
        self.save_merits()

    def load_storage(self):
        owner = self.owner
        for k, v in owner.storyteller_storage.iteritems():
            storage_dict = owner.attributes.get(v, dict())
            if not storage_dict:
                owner.attributes.add(v, storage_dict)
                storage_dict = owner.attributes.get(v)
            self.data_dict[k] = storage_dict

    def load_template(self):
        owner = self.owner
        valid_templates = owner.storyteller_templates
        save_data = self.data_dict['template']
        if not len(save_data):
            key = 'mortal'
        else:
            key = save_data.keys()[0]
            if key not in valid_templates.keys():
                key = 'mortal'
        self.template = Template(key=key, handler=self)
        self.save_template()

    def save_template(self):
        self.template.save()

    def swap_template(self, key=None):
        if not key:
            raise ValueError("No template entered to swap to!")
        find_template = partial_match(key, self.owner.storyteller_templates.keys())
        if not find_template:
            raise ValueError("Could not find a '%s' template." % key)
        self.template = Template(find_template, self)
        self.save_template()
        self.load_pools()
        self.load_sheet()


    def load_stats(self):
        owner = self.owner
        init_stats = list()
        for key in owner.storyteller_stats.keys():
            stat = Stat(key=key, handler=self)
            init_stats.append(stat)
            self.stats_dict[key] = stat
            self.stats_values[key] = int(stat)
        self.stats = sorted(init_stats, key=lambda stat: stat.list_order)
        stat_types = list(set([stat.kind for stat in self.stats]))
        for kind in stat_types:
            self.stats_type[kind] = tuple(sorted([stat for stat in self.stats if stat.kind == kind],
                                                 key=lambda stat2: stat2.list_order))

    def save_stats(self):
        for stat in self.stats: stat.save()

    def load_pools(self):
        pools = list()
        for key in self.template.pools.keys():
            pool = Pool(key=key, handler=self)
            pools.append(pool)
        self.pools = sorted(pools, key=lambda order: order.list_order)

    def save_pools(self):
        for pool in self.pools: pool.save()

    def load_custom(self):
        save_data = self.data_dict['custom']
        init_stats = list()
        for k, v in save_data.iteritems():
            stat = CustomStat(key=k, handler=self)
            init_stats.append(stat)
        self.custom = sorted(init_stats, key=lambda entry: entry.list_order)

    def save_custom(self):
        for custom in self.custom: custom.save()

    def load_merits(self):
        save_data = self.data_dict['merit']
        init_merits = list()
        for k, v in save_data.iteritems():
            merit = Merit(key=k, handler=self)
            init_merits.append(merit)
        self.merits = init_merits

    def save_merits(self):
        for merit in self.merits: merit.save()

    def load_powers(self):
        save_data = self.data_dict['power']
        init_powers = list()
        for k, v in save_data.iteritems():
            power = Power(key=k, handler=self)
            init_powers.append(power)
        self.powers = init_powers

    def save_powers(self):
        for power in self.powers: power.save()

    def load_sheet(self):
        self.sheet_sections = list()
        for section in self.owner.storyteller_sheet:
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


class StorytellerProperty(object):
    """
    This provides logic for the other Stat classes. It is not used directly.
    """
    key = 'Unset'
    handler = None
    save_type = 'Unset'
    name = 'Unset'
    category = 'Unset'
    sub_category = 'Unset'
    kind = 'Unset'
    save_fields = ()
    list_order = 1
    features = set()
    features_default = ()
    features_add = ()
    features_remove = ()

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    def __init__(self, key, handler):
        self.key = key
        self.owner = handler.owner
        self.handler = handler
        self.load()
        self.init_features()

    def init_features(self):
        default_set = set(self.features_default)
        remove_set = set(self.features_remove)
        add_set = set(self.features_add)
        final_set = default_set.union(add_set)
        self.features = tuple(final_set.difference(remove_set))

    @property
    def save_key(self):
        return self.key

    @property
    def saver(self):
        return self.handler.data_dict[self.save_type]

    def export(self):
        return {field: getattr(self, field) for field in self.save_fields}

    def save(self):
        self.saver[self.save_key] = self.export()

    def load(self):
        save_data = self.saver.get(self.save_key, dict())
        for k, v in save_data.iteritems():
            setattr(self, k, v)

class Template(StorytellerProperty):
    save_type = 'template'
    info_defaults = dict()
    info_save = dict()
    info_choices = dict()
    info_fields = dict()
    pools = dict()
    base_sheet_colors = {'title': 'n', 'border': 'n', 'textfield': 'n', 'texthead': 'n', 'colon': 'n',
                         'section_name': 'n', '3_column_name': 'n', 'advantage_name': 'n', 'advantage_border': 'n',
                         'slash': 'n', 'statdot': 'n', 'statfill': 'n', 'statname': 'n', 'damagename': 'n',
                         'damagetotal': 'n', 'damagetotalnum': 'n'}
    extra_sheet_colors = dict()
    sheet_column_1 = tuple()
    sheet_column_2 = tuple()
    save_fields = ('info_save',)
    sheet_footer = ''

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __nonzero__(self):
        return True

    def load(self):
        owner = self.owner
        save_data = self.saver.get(self.save_key, dict())
        child_data = owner.storyteller_templates[self.key]
        ancestor_data = dict(owner.storyteller_ancestors[self.save_type])
        parent_data = owner.storyteller_parents[self.save_type][child_data['parent']]
        ancestor_data.update(parent_data)
        ancestor_data.update(child_data)
        ancestor_data.update(save_data)
        for k, v in ancestor_data.iteritems():
            setattr(self, k, v)

    @property
    def info(self):
        info_dict = dict()
        info_dict.update(self.info_defaults)
        info_dict.update(self.info_save)
        return info_dict

    def get(self, field=None):
        if not field:
            return
        try:
            response = self.info[field]
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
                self.info_save.pop(found_field)
            except KeyError:
                return True
        if found_field in self.info_choices:
            choices = self.info_choices[found_field]
            find_value = partial_match(value, choices)
            if not find_value:
                raise KeyError("'%s' is not a valid entry for %s. Choices are: %s" % (value, found_field,
                                                                                          ', '.join(choices)))
            self.info_save[found_field] = find_value
        else:
            self.info_save[found_field] = sanitize_string(value)
        self.save()

class Stat(StorytellerProperty):
    """
    This class is used for all of the 'default' stats provided by a Storyteller game. Attributes, Skills, etc.
    """
    save_type = 'stat'
    _favored = False
    _supernal = False
    _epic = False
    _rating = 1
    _specialties = dict()
    save_fields = ('_rating', '_favored', '_supernal', '_epic', '_specialties')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<%s: %s - (%s)>' % (type(self).__name__, self.name, self._rating)

    def __hash__(self):
        return hash(self.key)

    def __int__(self):
        return self.rating

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.__name

    def __add__(self, other):
        return int(self) + int(other)

    def __radd__(self, other):
        return int(self) + int(other)

    def load(self):
        owner = self.owner
        save_data = self.saver.get(self.save_key, dict())
        child_data = owner.storyteller_stats[self.save_key]
        ancestor_data = dict(owner.storyteller_ancestors[self.save_type])
        parent_data = owner.storyteller_parents[self.save_type][child_data['parent']]
        ancestor_data.update(parent_data)
        ancestor_data.update(child_data)
        ancestor_data.update(save_data)
        for k, v in ancestor_data.iteritems():
            setattr(self, k, v)

    def save(self):
        super(Stat, self).save()
        self.handler.stats_values[self.save_key] = self.rating

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if 'dot' not in self.features:
            raise ValueError("'%s' cannot be purchased directly." % self)
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("'%s' must be set to a positive integer." % self)
        if not new_value >= 0:
            raise ValueError("'%s' must be set to a positive integer." % self)
        if self._rating == new_value:
            return
        self._rating = new_value
        self.save()

    @property
    def favored(self):
        return self._favored

    @favored.setter
    def favored(self, value):
        if 'favor' not in self.features:
            raise ValueError("'%s' cannot be set Favored." % self)
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("'%s' Favored must be set to 0 or 1." % self)
        if new_value not in [0, 1]:
            raise ValueError("'%s' Favored must be set to 0 or 1." % self)
        self._favored = bool(new_value)
        self.save()

    @property
    def supernal(self):
        return self._supernal

    @supernal.setter
    def supernal(self, value):
        if 'supernal' not in self.features:
            raise ValueError("'%s' cannot be set Supernal." % self)
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("'%s' Supernal must be set to 0 or 1." % self)
        if new_value not in [0, 1]:
            raise ValueError("'%s' Supernal must be set to 0 or 1." % self)
        self._supernal = bool(new_value)
        self.save()

    @property
    def epic(self):
        return self._epic

    @epic.setter
    def epic(self, value):
        if 'epic' not in self.features:
            raise ValueError("'%s' cannot be set Epic." % self)
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("'%s' Epic must be set to 0 or 1." % self)
        if new_value not in [0, 1]:
            raise ValueError("'%s' Epic must be set to 0 or 1." % self)
        self._epic = bool(new_value)
        self.save()

    def set_specialty(self, name, value):
        name = name.lower()
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("Specialties must be set to whole numbers.")
        if not new_value >= 0:
            raise ValueError("Specialties cannot be negative numbers.")
        if new_value == 0 and name in self._specialties.keys():
            self._specialties.pop(name, None)
            return
        self._specialties[name] = new_value
        self.save()

    def display(self):
        return int(self) or self.favored or self.supernal or self.favored or self.epic

    def sheet_format(self, width=23, no_favored=False, fill_char='.', colors=None):
        if not colors:
            colors = {'statname': 'n', 'statfill': 'n', 'statdot': 'n'}
        display_name = ANSIString('{%s%s{n' % (colors['statname'], self.name))
        if self.supernal:
            fav_dot = ANSIString('{r*{n')
        elif self.favored:
            fav_dot = ANSIString('{r+{n')
        else:
            fav_dot = ANSIString(' ')
        if not no_favored:
            display_name = fav_dot + display_name
        if self.rating > width - len(display_name) - 1:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], self.rating))
        else:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], '*' * self.rating))
        fill_length = width - len(display_name) - len(dot_display)
        fill = ANSIString('{%s%s{n' % (colors['statfill'], fill_char * fill_length))
        return display_name + fill + dot_display

    def sheet_specialties(self, width=35, fill_char='.', colors=None):
        if not colors:
            colors = {'statname': 'n', 'statfill': 'n', 'statdot': 'n'}
        specialty_list = list()
        for specialty, value in self._specialties.iteritems():
            display_name = ANSIString('{%s%s/%s{n' % (colors['statname'], self.name,
                                                      dramatic_capitalize(specialty)))
            if value > width - len(display_name) - 1:
                dot_display = ANSIString('{%s%s{n' % (colors['statdot'], self.rating))
            else:
                dot_display = ANSIString('{%s%s{n' % (colors['statdot'], '*' * self.rating))
            fill_length = width - len(display_name) - len(dot_display)
            fill = ANSIString('{%s%s{n' % (colors['statfill'], fill_char * fill_length))
            specialty_display = display_name + fill + dot_display
            specialty_list.append(specialty_display)
        return specialty_list


class CustomStat(Stat):
    """
    This class is used for all of the custom stats like Crafts or Styles..
    """
    save_type = 'custom'

    def __init__(self, key, handler):
        self.kind = key[0]
        self.name = dramatic_capitalize(key[1])
        super(CustomStat, self).__init__(key=key[1].lower(), handler=handler)
        self.parent = key[0]


    def load(self):
        owner = self.owner
        save_data = self.saver.get(self.save_key, dict())
        child_data = owner.storyteller_custom[self.kind]
        ancestor_data = dict(owner.storyteller_ancestors['custom'])
        parent_data = owner.storyteller_parents['custom'][child_data['parent']]
        ancestor_data.update(parent_data)
        ancestor_data.update(child_data)
        ancestor_data.update(save_data)
        for k, v in ancestor_data.iteritems():
            setattr(self, k, v)

    @property
    def save_key(self):
        return (self.kind, self.name)


class Merit(StorytellerProperty):
    name = None
    save_type = 'merit'
    _description = None
    _notes = None
    _rating = 0
    kind = 'merit'
    save_fields = ('_rating', '_description', '_notes')

    def __init__(self, key, handler):
        self.key = key[2]
        self.owner = handler.owner
        self.handler = handler
        self.kind = key[0]
        self.category = dramatic_capitalize(key[1])
        if key[2]:
            self.name = dramatic_capitalize(self.key)
            self.key = self.name
        self.load()
        self.init_features()


    def __repr__(self):
        return '%s: %s: %s (%s)' % (self.kind, self.category, self.name, self.rating)

    @property
    def display_name(self):
        if not self.name:
            name_string = self.category
        else:
            name_string = '%s: %s' % (self.category, self.name)
        return name_string

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        try:
            new_value = int(value)
        except ValueError:
            raise ValueError("'%s' must be set to a positive integer." % self)
        if not new_value >= 0:
            raise ValueError("'%s' must be set to a positive integer." % self)
        if self._rating == new_value:
            return
        self._rating = new_value
        self.save()

    def load(self):
        owner = self.owner
        save_data = self.saver.get(self.save_key, dict())
        child_data = owner.storyteller_merits[self.kind]
        ancestor_data = dict(owner.storyteller_ancestors[self.save_type])
        parent_data = owner.storyteller_parents[self.save_type][child_data['parent']]
        ancestor_data.update(parent_data)
        ancestor_data.update(child_data)
        ancestor_data.update(save_data)
        for k, v in ancestor_data.iteritems():
            setattr(self, k, v)

    def sheet_format(self, width=23, fill_char='.', colors=None):
        if not colors:
            colors = {'statname': 'n', 'statfill': 'n', 'statdot': 'n'}
        display_name = ANSIString('{%s%s{n' % (colors['statname'], self.display_name))
        if self.rating > width - len(display_name) - 1:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], self.rating))
        else:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], '*' * self.rating))
        fill_length = width - len(display_name) - len(dot_display)
        fill = ANSIString('{%s%s{n' % (colors['statfill'], fill_char * fill_length))
        return display_name + fill + dot_display

    @property
    def save_key(self):
        return (self.kind, dramatic_capitalize(self.category), dramatic_capitalize(self.name) if self.name else None)


class Power(StorytellerProperty):
    save_type = 'power'
    kind = 'power'
    _rating = 1
    save_fields = ('_rating',)

    def __init__(self, key, handler):
        self.kind = key[0]
        super(Power, self).__init__(key=key[2], handler=handler)
        self.sub_category = key[1]
        self.key = dramatic_capitalize(self.key)

    def __int__(self):
        return self.rating

    def __repr__(self):
        return '<%s: %s (%s)>' % (self.kind, self.key, self.rating)

    @property
    def rating(self):
        return self._rating

    def load(self):
        owner = self.owner
        save_data = self.handler.data_dict[self.save_type].get(self.save_key, dict())
        child_data = owner.storyteller_powers[self.kind]
        ancestor_data = dict(owner.storyteller_ancestors[self.save_type])
        parent_data = owner.storyteller_parents[self.save_type][child_data['parent']]
        ancestor_data.update(parent_data)
        ancestor_data.update(child_data)
        ancestor_data.update(save_data)
        for k, v in ancestor_data.iteritems():
            setattr(self, k, v)

    def sheet_format(self, width=23, colors=None, mode='stat'):
        if mode == 'stat':
            return self.stat_format(width, colors)
        if mode == 'word':
            return self.word_format(width, colors)

    def word_format(self, width, colors):
        if self._rating > 1:
            return '%s (%s)' % (self.key, self._rating)
        else:
            return self.key

    def stat_format(self, width, colors):
        pass

    @property
    def save_key(self):
        return (self.kind, self.sub_category, self.key)

class Pool(StorytellerProperty):
    save_type = 'pool'
    unit = 'Points'
    refresh = 'max'
    features_default = ('gain', 'spend', 'refresh', 'commit')
    save_fields = ('_commits', '_points')
    _commits = dict()
    _points = 0
    _func = None

    def __repr__(self):
        return '<%s: %s/%s>' % (self.name, self.available, self.max)

    def __int__(self):
        return self.available

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __init__(self, key, handler):
        super(Pool, self).__init__(key, handler)
        self._func = handler.template.pools[key]

    def load(self):
        owner = self.owner
        save_data = self.handler.data_dict[self.save_type].get(self.save_key, dict())
        child_data = owner.storyteller_pools[self.key]
        ancestor_data = dict(owner.storyteller_ancestors[self.save_type])
        parent_data = owner.storyteller_parents[self.save_type][child_data['parent']]
        ancestor_data.update(parent_data)
        ancestor_data.update(child_data)
        ancestor_data.update(save_data)
        for k, v in ancestor_data.iteritems():
            setattr(self, k, v)

    @property
    def max(self):
        return self._func(self.handler)

    @property
    def available(self):
        return min(self._points, self.max - self.total_commit)

    @property
    def total_commit(self):
        return sum(self._commits.values())

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
        if reason.lower() in [key.lower() for key in self._commits.keys()]:
            raise ValueError("Commitments must be unique.")
        self._commits[reason] = value
        self._points -= value
        return True

    def uncommit(self, reason=None):
        if not reason:
            raise ValueError("Reason is empty!")
        find_reason = partial_match(reason, self._commits.keys())
        if not find_reason:
            raise ValueError("Commitment not found.")
        self._commits.pop(find_reason)
        return True

    def fill(self, amount=None):
        try:
            value = int(amount)
        except ValueError:
            raise ValueError("Values must be integers.")
        if not value > 0:
            raise ValueError("Values must be positive.")
        self._points = min(self._points + value, self.max - self.total_commit)
        return True

    def drain(self, amount=None):
        try:
            value = int(amount)
        except ValueError:
            raise ValueError("Values must be integers.")
        if not value > 0:
            raise ValueError("Values must be positive.")
        if value > self._points:
            raise ValueError("There aren't that many %s to spend!" % self.unit)
        self._points -= value
        return True

    def refresh_pool(self):
        if self.refresh == 'max':
            self._points = self.max - self.total_commit
            return
        if self.refresh == 'empty':
            self._points = 0
            return

    def sheet_format(self, rjust=None, zfill=2):
        val_string = '%s/%s' % (str(self._points).zfill(zfill), str(self.max).zfill(zfill))
        if rjust:
            return '%s: %s' % (self.name.rjust(rjust), val_string)
        else:
            return '%s: %s' % (self.name, val_string)