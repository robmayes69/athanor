from commands.library import AthanorError, dramatic_capitalize, sanitize_string, partial_match
from evennia.utils.utils import make_iter
from world.storyteller.stats import Stat

class StatPower(object):

    __slots__ = ['base_name', 'game_category', 'sub_category', 'can_roll', '_value', '_supernal', '_favored',
                 'default_add', 'initial_value', 'custom_name', 'main_category', 'list_order', 'linked_stat',
                 '_stat', '_stat_name', 'default_stat', 'can_stat', 'custom_category']

    base_name = 'StatPower'
    custom_name = None
    custom_category = None
    game_category = 'Storyteller'
    main_category = None
    sub_category = None
    can_roll = False
    can_stat = False
    initial_value = None
    list_order = 0
    default_stat = None
    _value = 0
    _favored = False
    _supernal = False
    _stat = None
    _stat_name = None

    def __init__(self, name=None):
        if not name:
            raise AthanorError("A '%s' needs a name!")
        self.custom_name = dramatic_capitalize(sanitize_string(name))


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
        return (type(self) == type(other)) and self.full_name == other.full_name

    def __hash__(self):
        return str(self).__hash__() + self.base_name.__hash__()

    def __add__(self, other):
        return int(self) + int(other)

    def __radd__(self, other):
        return int(self) + int(other)

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
        return self._stat.current_favored

    @property
    def current_supernal(self):
        return self._stat.current_supernal

    @property
    def linked_stat(self):
        return self._stat

    @linked_stat.setter
    def linked_stat(self, value):
        if not value:
            self._stat = None
            return
        if not isinstance(value, Stat):
            raise AthanorError("A %s can only be linked to Stat instances." % self.base_name)
        self._stat = value


class WordPower(StatPower):
    base_name = 'WordPower'


    def __init__(self, name=None, category=None):
        if not name:
            raise AthanorError("A '%s' needs a name!")
        if '#' in name:
            try:
                name, value = name.split('#', 1)
                value = int(value)
            except ValueError:
                raise AthanorError("Invalid multiple purchase entry for '%s'!" % name)
        else:
            value = 1
        self.custom_name = dramatic_capitalize(sanitize_string(name))
        self._value = value
        if category:
            self.custom_category = dramatic_capitalize(sanitize_string(category))



class AdvantageHandler(object):

    __slots__ = ['owner', 'valid_classes', 'valid_classes_dict', 'cache_advantages']

    def __init__(self, owner):
        self.owner = owner
        self.valid_classes = None
        self.valid_classes_dict = dict()
        self.cache_advantages = None
        self.load()

    def load(self):
        load_db = self.owner.storage_locations['advantages']
        load_advantages = set(self.owner.attributes.get(load_db, []))
        self.valid_classes = set(self.owner.valid_advantages)

        for custom in self.valid_classes:
            self.valid_classes_dict[custom.base_name] = custom
        for stat in load_advantages:
            if stat.__class__ not in self.valid_classes:
                load_advantages.remove(stat)
        search_advantages = sorted([stat for stat in list(load_advantages)], key=lambda stat2: str(stat2))
        self.cache_advantages = set(search_advantages)

        for stat in [adv for adv in self.cache_advantages if adv.can_stat]:
            try:
                if stat.default_stat:
                    stat_search = stat.default_stat
                else:
                    stat_search = stat._stat_name
                stat.linked_stat = self.owner.stats.stats_dict[stat_search]
            except AthanorError:
                self.owner.sys_msg(message="You have a corruption error with Custom Stat '%s/%s'. "
                                           "Please contact staff." % (stat.base_name, stat.custom_name), error=True,
                                   sys_name='EDITCHAR')

    def add(self, custom_type=None, stat=None, name=None, value=None, caller=None):
        if not caller:
            caller = self.owner
        if not custom_type:
            raise AthanorError("What kind of Custom Stat are you setting?")
        found_name = partial_match(custom_type, self.valid_classes_dict.keys())
        if not found_name:
            raise AthanorError("Custom Stat '%s' not found." % custom_type)
        found_custom = self.valid_classes_dict[found_name]
        if found_custom.default_stat:
            found_stat = self.owner.stats.stats_dict[found_custom.default_stat]
        else:
            if not stat:
                raise AthanorError("A %s requires a Stat." % found_custom.base_name)
            found_stat = partial_match(stat, found_custom.valid_stats(self.owner))
        if not found_stat:
            raise AthanorError("Cannot set %s. No stat found." % found_custom.base_name)



    def save(self, no_load=False):
        load_db = self.owner.storage_locations['advantages']
        self.owner.attributes.add(load_db, set(self.cache_advantages))
        if no_load:
            return
        self.load()