from commands.library import AthanorError, partial_match, sanitize_string, dramatic_capitalize
from evennia.utils.utils import make_iter
from evennia.utils.ansi import ANSIString


class Stat(object):

    __slots__ = ['base_name', 'game_category', 'sub_category', 'can_favor', 'can_supernal', 'can_specialize',
                 'can_roll', 'can_bonus', 'current_bonus', 'initial_value', 'custom_name', 'main_category',
                 'list_order', '_value', '_supernal', '_favored', 'can_set', 'specialties', 'always_display', '_epic',
                 'can_epic', 'never_display']

    base_name = 'DefaultStat'
    custom_name = None
    game_category = 'Storyteller'
    main_category = None
    sub_category = None
    can_favor = False
    can_supernal = False
    can_set = True
    can_specialize = False
    can_roll = False
    can_bonus = False
    can_epic = False
    current_bonus = 0
    initial_value = None
    list_order = 0
    specialties = dict()
    always_display = False
    never_display = False
    _value = 0
    _supernal = False
    _favored = False
    _epic = 0

    def __init__(self):
        try:
            self.current_value = self.initial_value
        except AthanorError:
            self._value = self.initial_value

    def __unicode__(self):
        return unicode(self.full_name)

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return '<%s: %s - (%s)>' % (self.main_category, self.full_name, self.display_rank)

    def __nonzero__(self):
        return True

    def __int__(self):
        return self.roll_value

    def __eq__(self, other):
        return type(self) == type(other)

    def __hash__(self):
        return self.base_name.__hash__()

    def __add__(self, other):
        return int(self) + int(other)

    def __radd__(self, other):
        return int(self) + int(other)

    @property
    def current_value(self):
        return self._value

    @current_value.setter
    def current_value(self, value):
        try:
            new_value = int(value)
        except ValueError:
            raise AthanorError("'%s' must be set to a positive integer." % self)
        if not new_value >= 0:
            raise AthanorError("'%s' must be set to a positive integer." % self)
        self._value = new_value

    @property
    def current_favored(self):
        return self._favored

    @current_favored.setter
    def current_favored(self, value):
        if not self.can_favor:
            raise AthanorError("'%s' cannot be set Favored." % self)
        try:
            new_value = int(value)
        except ValueError:
            raise AthanorError("'%s' Favored must be set to 0 or 1." % self)
        if new_value not in [0, 1]:
            raise AthanorError("'%s' Favored must be set to 0 or 1." % self)
        self._favored = bool(new_value)

    @property
    def current_supernal(self):
        return self._supernal

    @current_supernal.setter
    def current_supernal(self, value):
        if not self.can_supernal:
            raise AthanorError("'%s' cannot be set Supernal." % self)
        try:
            new_value = int(value)
        except ValueError:
            raise AthanorError("'%s' Supernal must be set to 0 or 1." % self)
        if new_value not in [0, 1]:
            raise AthanorError("'%s' Supernal must be set to 0 or 1." % self)
        self._supernal = bool(new_value)

    @property
    def full_name(self):
        return self.custom_name or self.base_name

    @property
    def display_rank(self):
        return str(self.current_value or 0)

    @property
    def roll_value(self):
        return (self.natural_rank + self.bonus_rank) or 0

    @property
    def natural_rank(self):
        return max(make_iter(self.current_value))

    @property
    def bonus_rank(self):
        return self.current_bonus

    def should_display(self):
        if self.never_display:
            return False
        if self.always_display:
            return True
        if self.current_supernal or self.current_favored or self.current_value:
            return True
        return False

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


class Attribute(Stat):
    base_name = 'Attribute'
    main_category = 'Attribute'
    can_roll = True
    initial_value = 1
    always_display = True

class Skill(Stat):
    base_name = 'Skill'
    main_category = 'Skill'
    can_roll = True
    initial_value = 0


class Power(Stat):
    base_name = 'Power'
    main_category = 'Advantage'
    can_roll = True
    initial_value = 1
    never_display = True

class Willpower(Stat):
    base_name = 'Willpower'
    main_category = 'Advantage'
    can_roll = True
    initial_value = 5
    never_display = True



class StatHandler(object):

    __slots__ = ['owner', 'valid_classes', 'cache_stats', 'stats_dict', 'attribute_stats', 'attributes_physical',
                 'attributes_social', 'attributes_mental', 'skill_stats', 'skills_physical', 'skills_social',
                 'skills_mental', 'virtue_stats', 'favorable_stats', 'supernable_stats', 'specialize_stats',
                 'specialized_stats']

    def __init__(self, owner):
        self.owner = owner
        self.valid_classes = list()
        self.stats_dict = dict()
        self.cache_stats = None
        self.attribute_stats = list()
        self.attributes_physical = list()
        self.attributes_social = list()
        self.attributes_mental = list()
        self.skill_stats = list()
        self.skills_physical = list()
        self.skills_social = list()
        self.skills_mental = list()
        self.virtue_stats = list()
        self.favorable_stats = list()
        self.supernable_stats = list()
        self.specialize_stats = list()
        self.specialized_stats = list()
        self.load()

    def load(self):
        load_db = self.owner.storage_locations['stats']
        load_stats = set(self.owner.attributes.get(load_db, []))
        expected_power = self.owner.template.power
        self.valid_classes = list(self.owner.valid_stats)
        self.valid_classes.append(expected_power)
        new_stats = set([stat() for stat in self.valid_classes])
        if not load_stats == new_stats:
            load_stats.update(new_stats)
            load_stats = new_stats.intersection(load_stats)
        self.cache_stats = sorted(list(load_stats), key=lambda stat: stat.list_order)
        attribute_stats, attributes_physical, attributes_social, attributes_mental = [list(), list(), list(), list()]
        skill_stats, skills_physical, skills_social, skills_mental = [list(), list(), list(), list()]
        virtue_stats, favorable_stats, supernable_stats, specialize_stats, specialized_stats = [list(), list(), list(),
                                                                                                list(), list()]

        for stat in self.cache_stats:
            self.stats_dict[stat.base_name] = stat
            if stat.main_category == 'Attribute':
                attribute_stats.append(stat)
                if stat.sub_category == 'Physical':
                    attributes_physical.append(stat)
                if stat.sub_category == 'Social':
                    attributes_social.append(stat)
                if stat.sub_category == 'Mental':
                    attributes_mental.append(stat)

            if stat.main_category == 'Skill':
                skill_stats.append(stat)
                if stat.sub_category == 'Physical':
                    skills_physical.append(stat)
                if stat.sub_category == 'Social':
                    skills_social.append(stat)
                if stat.main_category == 'Mental':
                    attributes_mental.append(stat)

            if stat.main_category == 'Virtue':
                virtue_stats.append(stat)

            if stat.can_favor:
                favorable_stats.append(stat)
            if stat.can_supernal:
                supernable_stats.append(stat)
            if stat.can_specialize:
                specialize_stats.append(stat)
            if stat.specialties:
                specialized_stats.append(stat)

        self.attribute_stats = tuple(attribute_stats)
        self.attributes_physical = tuple(attributes_physical)
        self.attributes_social = tuple(attributes_social)
        self.attributes_mental = tuple(attributes_mental)

        self.skill_stats = tuple(skill_stats)
        self.skills_physical = tuple(skills_physical)
        self.skills_social = tuple(skills_social)
        self.skills_mental = tuple(skills_mental)

        self.favorable_stats = tuple(favorable_stats)
        self.supernable_stats = tuple(supernable_stats)
        self.specialize_stats = tuple(specialize_stats)
        self.specialized_stats = tuple(specialized_stats)

    def all(self):
        return self.cache_stats

    def add(self, new_stat=None):
        if not new_stat:
            return
        stat_list = make_iter(new_stat)
        for stat in stat_list:
            if not isinstance(stat, Stat):
                raise AthanorError("StatHandler expects a Stat-type object, received %s" % type(stat))
            self.cache_stats.add(stat)
        self.save()

    def save(self, no_load=False):
        load_db = self.owner.storage_locations['stats']
        self.owner.attributes.add(load_db, self.cache_stats)
        if no_load:
            return
        self.load()

    def set(self, stat=None, value=None, caller=None):
        if not caller:
            caller = self.owner
        if not stat:
            raise AthanorError("No stat entered to set.")
        if not value:
            raise AthanorError("Nothing entered to set it to.")
        find_stat = partial_match(stat, self.cache_stats)
        if not find_stat:
            raise AthanorError("Stat '%s' not found." % stat)
        try:
            find_stat.current_value = value
        except AthanorError as err:
            caller.sys_msg(message=str(err), error=True, sys_name='EDITCHAR')
            return
        else:
            caller.sys_msg(message='Your %s stat is now: %s' % (find_stat, find_stat.current_value),
                           sys_name='EDITCHAR')
            self.save()
            return True

