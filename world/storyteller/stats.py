from commands.library import AthanorError, partial_match
from evennia.utils.utils import make_iter

class Stat(object):

    __slots__ = ['base_name', 'game_category', 'sub_category', 'can_favor', 'can_supernal', 'can_specialize',
                 'can_roll', 'can_bonus', 'current_bonus', 'initial_value', 'custom_name', 'main_category',
                 'list_order', '_value', '_supernal', '_favored', 'can_set']

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
    current_bonus = 0
    initial_value = None
    list_order = 0
    _value = None
    _supernal = None
    _favored = None

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
        self._favored = new_value

    @property
    def current_supernal(self):
        return self._favored

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
        self._supernal = new_value


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


class Attribute(Stat):
    base_name = 'Attribute'
    main_category = 'Attribute'
    can_roll = True
    initial_value = 1


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


class Willpower(Stat):
    base_name = 'Willpower'
    main_category = 'Advantage'
    can_roll = True
    initial_value = 5

class CustomStat(object):

    __slots__ = ['base_name', 'game_category', 'sub_category',
                 'can_roll', 'current_value', 'current_favored', 'current_supernal',
                 'default_add', 'initial_value', 'custom_name', 'main_category', 'list_order']

    base_name = 'CustomStat'
    custom_name = None
    game_category = 'Storyteller'
    main_category = None
    sub_category = None
    can_roll = False
    current_value = None
    current_favored = False
    current_supernal = False
    default_add = False
    initial_value = None
    list_order = 0


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

    @property
    def full_name(self):
        return self.custom_name or self.base_name

    @property
    def display_rank(self):
        return str(self.current_value or 0)

    @property
    def roll_value(self):
        return self.natural_rank or 0

    @property
    def natural_rank(self):
        return max(make_iter(self.current_value))


class StatHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.load()
        self.save(no_load=True)

    def load(self):
        load_db = self.owner.storage_locations['stats']
        load_stats = list(self.owner.attributes.get(load_db, []))
        expected_power = self.owner.storyteller_template.power
        self.valid_classes = list(self.owner.valid_stats)
        self.valid_classes.append(expected_power)
        for stat in load_stats:
            if stat.__class__ not in self.valid_classes:
                load_stats.remove(stat)
        used_classes = [stat.__class__ for stat in load_stats]
        for stat_class in self.valid_classes:
            if stat_class not in used_classes:
                load_stats.append(stat_class())
        self.cache_stats = load_stats
        self.stats_dict = dict()
        for stat in self.cache_stats:
            self.stats_dict[stat.base_name] = stat
        self.attribute_stats = sorted([stat for stat in self.cache_stats if stat.main_category == 'Attribute'],
                                      key=lambda stat2: stat2.list_order)
        self.attributes_physical = [stat for stat in self.attribute_stats if stat.sub_category == 'Physical']
        self.attributes_social = [stat for stat in self.attribute_stats if stat.sub_category == 'Social']
        self.attributes_mental = [stat for stat in self.attribute_stats if stat.sub_category == 'Mental']
        self.skill_stats = sorted([stat for stat in self.cache_stats if stat.main_category == 'Skill'],
                                  key=lambda stat2: stat2.list_order)
        self.skills_physical = [stat for stat in self.skill_stats if stat.sub_category == 'Physical']
        self.skills_social = [stat for stat in self.skill_stats if stat.sub_category == 'Social']
        self.skills_mental = [stat for stat in self.skill_stats if stat.sub_category == 'Mental']
        self.virtue_stats = sorted([stat for stat in self.cache_stats if stat.main_category == 'Virtue'],
                                   key=lambda stat2: stat2.list_order)

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

class CustomHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.load()
        self.save(no_load=True)

    def load(self):
        pass

    def save(self, no_load=False):
        pass