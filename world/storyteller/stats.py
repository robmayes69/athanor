from commands.library import AthanorError
from evennia.utils.utils import make_iter

class Stat(object):

    __slots__ = ['base_name', 'game_category', 'sub_category', 'can_favor', 'can_supernal', 'can_specialize',
                 'can_roll', 'can_bonus', 'current_bonus', 'current_value', 'current_favored', 'current_supernal',
                 'initial_value', 'custom_name', 'main_category', 'list_order']

    base_name = 'DefaultStat'
    custom_name = None
    game_category = 'Storyteller'
    main_category = None
    sub_category = None
    can_favor = False
    can_supernal = False
    can_specialize = False
    can_roll = False
    can_bonus = False
    current_bonus = 0
    current_value = None
    current_favored = False
    current_supernal = False
    initial_value = None
    list_order = 0

    def __init__(self):
        self.current_value = self.initial_value

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


class CustomHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.load()
        self.save(no_load=True)

    def load(self):
        pass

    def save(self, no_load=False):
        pass