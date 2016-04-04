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

    def __init__(self, owner):
        self.owner = owner
        self.colors = self.sheet_colors
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
        color_dict.update(self.owner.ndb.template.base_sheet_colors)
        color_dict.update(self.owner.ndb.template.extra_sheet_colors)
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
    section_type = 'Stat'

    def load(self):
        self.choices = self.owner.ndb.stats_all

    def save(self):
        self.owner.storyteller.save_stats()

    def all(self):
        return self.choices


class Attributes(StatSection):
    base_name = 'Attributes'
    section_type = 'Attribute'
    list_order = 10
    physical = tuple()
    social = tuple()
    mental = tuple()

    def load(self):
        self.choices = self.owner.ndb.stats_type['Attribute']
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
    section_type = 'Skill'
    list_order = 15

    def load(self):
        self.choices = self.owner.ndb.stats_type['skill']

    def sheet_render(self, width=78):
        colors = self.sheet_colors
        skills = [stat for stat in self.choices if stat.display]
        if not skills:
            return
        section = list()
        section.append(self.sheet_header(self.name, width=width))
        skill_display = [stat.sheet_format(width=23, colors=colors) for stat in skills]
        skill_table = tabular_table(skill_display, field_width=23, line_length=width-2)
        section.append(self.sheet_border(skill_table, width=width))
        return '\n'.join(unicode(line) for line in section)


class Specialties(StatSection):
    base_name = 'Specialties'
    section_type = 'Specialty'
    list_order = 16

    def load(self):
        self.choices = [stat for stat in self.owner.ndb.stats_all if 'special' in stat.features]
        self.specialized = [stat for stat in self.owner.ndb.stats_all if stat._specialties]

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
        self.choices = [stat for stat in self.owner.ndb.stats_all if 'favor' in stat.features]
        self.existing = [stat for stat in self.owner.ndb.stats_all if stat._favored]

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
        pass
        #self.existing = [power for power in self.owner.ndb.powers_all if isinstance(power, self.custom_type)]

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
        pass
        #self.existing = [power for power in self.owner.ndb.powers_all if isinstance(power, self.custom_type)]

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
        servername = unicode(settings.SERVERNAME)
        colors = self.sheet_colors
        line1 = '  {%s.%s.{n' % (colors['border'], '-' * (width-6))
        line2 = ' {%s/{n%s{n{%s\\{n' % (colors['border'], servername.center(width-4), colors['border'])
        line3 = self.sheet_header(width=width)
        name = self.owner.key
        power = self.owner.ndb.stats_dict['essence']
        powername = 'Essence'
        column_1 = ['Name']
        column_1 += self.owner.ndb.template.sheet_column_1
        column_2 = [powername]
        column_2 += self.owner.ndb.template.sheet_column_2
        column_1_len = max([len(entry) for entry in column_1])
        column_2_len = max([len(entry) for entry in column_2])
        column_1_prep = list()
        column_2_prep = list()
        for entry in column_1:
            if entry == 'Name':
                display = '%s: %s' % ('Name'.rjust(column_1_len), name)
            else:
                display = '%s: %s' % (entry.rjust(column_1_len), self.owner.ndb.template.get(entry))
            column_1_prep.append(display)
        for entry in column_2:
            if entry == powername:
                display = '%s: %s' % (powername.rjust(column_2_len), int(power))
            else:
                display = '%s: %s' % (entry.rjust(column_2_len), self.owner.ndb.template.get(entry))
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
    stats_dict = dict()
    stats_type = dict()
    owner = None
    custom = list()
    merits = list()
    pools = list()
    powers = list()
    sheet_sections = tuple()
    render_sections = tuple()

    def __repr__(self):
        return '<StorytellerHandler for %s>' % self.owner.key

    def __init__(self, owner):
        """
        'Owner' must be an instance of StorytellerCharacter.
        """
        self.owner = owner
        self.load()

    def load(self):
        self.load_template()
        self.load_stats()
        self.load_pools()
        self.load_custom()
        self.load_powers()
        #self.load_merits()
        self.load_sheet()

    def load_template(self):
        owner = self.owner
        valid_templates = owner.storyteller_templates
        db_name = owner.storyteller_storage['template']
        save_data = owner.attributes.get(db_name, dict())
        key = save_data.get('key', 'mortal')
        if key not in valid_templates.keys():
            key = 'mortal'
        self.template = Template(owner=owner, key=key, save_data=save_data)
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
            stat = Stat(owner=owner, key=key, save_data=save_data.get(key, dict()))
            init_stats.append(stat)
            self.stats_dict[key] = int(stat)
        self.stats = sorted(init_stats, key=lambda stat: stat.list_order)
        owner.ndb.stats_all = self.stats
        owner.ndb.stats_dict = self.stats_dict
        stat_types = list(set([stat.type for stat in self.stats]))
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

    def change_template(self, key=None):
        pass

    def load_pools(self):
        owner = self.owner
        db_name = owner.storyteller_storage['pools']
        save_data = owner.attributes.get(db_name, dict())
        pools = list()
        for key in owner.ndb.template.pools.keys():
            pool = Pool(owner=owner, key=key, save_data=save_data.get(key, dict()))
            pools.append(pool)
        self.pools = sorted(pools, key=lambda order: order.list_order)
        owner.ndb.pools = self.pools
        self.save_pools()

    def save_pools(self):
        owner = self.owner
        db_name = owner.storyteller_storage['pools']
        export_data = dict()
        for pool in self.pools:
            export_data[pool.key] = pool.export()
        owner.attributes.add(db_name, export_data)

    def load_custom(self):
        owner = self.owner
        db_name = owner.storyteller_storage['custom']
        save_data = owner.attributes.get(db_name, dict())
        init_stats = list()
        for k, v in save_data.iteritems():
            stat = CustomStat(owner=owner, key=k, save_data=v)
            init_stats.append(stat)
        self.custom = sorted(init_stats, key=lambda entry: entry.list_order)
        self.save_custom()

    def save_custom(self):
        owner = self.owner
        db_name = owner.storyteller_storage['custom']
        export_data = dict()
        for stat in self.custom:
            export_data[(stat.parent, stat.key)] = stat.export()
        owner.attributes.add(db_name, export_data)

    def set_custom(self, category, key, value):
        pass

    def load_merits(self):
        owner = self.owner
        db_name = owner.storyteller_storage['merits']
        save_data = owner.attributes.get(db_name, dict())
        init_merits = list()
        for k, v in save_data.iteritems():
            merit = Merit(owner=owner, key=k, save_data=v)
            init_merits.append(merit)
        self.merits = init_merits

    def save_merits(self):
        owner = self.owner
        db_name = owner.storyteller_storage['merits']
        export_data = dict()
        for merit in self.merits:
            export_data[(merit.type, merit.category, merit.name)] = {merit.export()}
        owner.attributes.add(db_name, export_data)

    def load_powers(self):
        owner = self.owner
        db_name = owner.storyteller_storage['powers']
        save_data = owner.attributes.get(db_name, dict())
        init_merits = list()
        for k, v in save_data.iteritems():
            merit = Power(owner=owner, key=k, save_data=v)
            init_merits.append(merit)
        self.merits = init_merits

    def save_powers(self):
        owner = self.owner
        db_name = owner.storyteller_storage['powers']
        export_data = dict()
        for power in self.powers:
            export_data[(power.type, power.category, power.sub_category, power.name)] = {power.export()}
        owner.attributes.add(db_name, export_data)

    def load_sheet(self):
        owner = self.owner
        self.sheet_sections = list()
        for section in owner.storyteller_sheet:
            self.sheet_sections.append(section(owner=owner))
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
    save_type = 'Unset'
    name = 'Unset'
    key = 'Unset'
    category = 'Unset'
    sub_category = 'Unset'
    type = 'Unset'
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

    def __init__(self, owner, key=None, save_data=None):
        if not save_data:
            save_data = dict()
        self.owner = owner
        self.key = key
        set_data = self.defaults(owner, key, save_data)
        for k, v in set_data.iteritems():
            setattr(self, k, v)
        default_set = set(self.features_default)
        remove_set = set(self.features_remove)
        add_set = set(self.features_add)
        final_set = default_set.union(add_set)
        self.features = tuple(final_set.difference(remove_set))

    def defaults(self, owner, key, save_data):
        child_data = owner.storyteller_stats[key]
        ancestor_data = dict(owner.storyteller_ancestors[self.save_type])
        parent_data = owner.storyteller_parents[self.save_type][child_data['parent']]
        ancestor_data.update(parent_data)
        ancestor_data.update(child_data)
        ancestor_data.update(save_data)
        return ancestor_data

    def export(self):
        export_dict = dict()
        for field in self.save_fields:
            export_dict[field] = getattr(self, field)
        return export_dict


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

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __nonzero__(self):
        return True

    @property
    def info(self):
        info_dict = dict()
        info_dict.update(self.info_defaults)
        info_dict.update(self.info_save)
        return info_dict

    def export(self):
        save_dict = dict()
        for field in self.save_fields:
            save_dict[field] = getattr(self, field)
        return save_dict

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
        self._rating = new_value

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

    def __init__(self, owner, key=None, save_data=None):
        super(CustomStat, self).__init__(owner, key=key[1], save_data=save_data)
        self.parent = key[0]

    def defaults(self, owner, key, save_data):
        child_data = owner.storyteller_stats[key]
        ancestor_data = dict(owner.storyteller_ancestors['custom'])
        parent_data = owner.storyteller_parents['custom'][child_data['parent']]
        ancestor_data.update(parent_data)
        ancestor_data.update(child_data)
        ancestor_data.update(save_data)
        return ancestor_data


class Merit(StorytellerProperty):
    pass


class Power(StorytellerProperty):
    pass


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

    def __init__(self, owner, key=None, save_data=None):
        super(Pool, self).__init__(owner, key, save_data)
        self._func = owner.ndb.template.pools[key]

    def defaults(self, owner, key, save_data):
        child_data = owner.storyteller_pools[key]
        ancestor_data = dict(owner.storyteller_ancestors['pool'])
        parent_data = owner.storyteller_parents['pool'][child_data['parent']]
        ancestor_data.update(parent_data)
        ancestor_data.update(child_data)
        ancestor_data.update(save_data)
        return ancestor_data

    @property
    def max(self):
        return self._func(self.owner)

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
        display_name = self.name
        if rjust:
            return '%s: %s' % (self.name.rjust(rjust), val_string)
        else:
            return '%s: %s' % (self.name, val_string)