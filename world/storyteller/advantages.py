from commands.library import AthanorError, dramatic_capitalize, sanitize_string, partial_match
from evennia.utils.utils import make_iter
from world.storyteller.stats import Stat

class StatPower(object):

    __slots__ = ['base_name', 'game_category', 'sub_category', 'can_roll', '_value', '_supernal', '_favored',
                 'default_add', 'initial_value', 'custom_name', 'main_category', 'list_order', 'linked_stat',
                 '_stat', '_stat_name', 'default_stat', 'can_stat', 'custom_category', 'available_subcategories']

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
    available_subcategories = list()
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

    def sheet_format(self):
        return self.full_name

class WordPower(StatPower):
    base_name = 'WordPower'


    def __init__(self, name=None, sub_category=None, custom_category=None):
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
        self.custom_name = dramatic_capitalize(sanitize_string(name, strip_ansi=True))
        self._value = value
        if sub_category:
            found_sub = partial_match(sub_category, self.available_subcategories)
            if not found_sub:
                raise AthanorError("Sub-category '%s' is not available!" % sub_category)
            self.sub_category = found_sub
        if custom_category:
            self.custom_category = dramatic_capitalize(sanitize_string(custom_category, strip_ansi=True))

    def sheet_format(self):
        if self.current_value > 1:
            return '%s (%s)' % (self.full_name, self.current_value)
        else:
            return self.full_name


class AdvantageHandler(object):

    __slots__ = ['owner', 'cache_advantages']

    def __init__(self, owner):
        self.owner = owner
        self.cache_advantages = None
        self.load()

    def load(self):
        load_db = self.owner.storage_locations['advantages']
        load_advantages = set(self.owner.attributes.get(load_db, []))
        search_advantages = [stat for stat in list(load_advantages) if isinstance(stat, StatPower)]
        self.cache_advantages = set(search_advantages)

    def add(self, new_advantage=None):
        if not new_advantage:
            return
        stat_list = make_iter(new_advantage)
        for stat in stat_list:
            if not isinstance(stat, StatPower):
                raise AthanorError("AdvantageHandler expects a Power-type object, received %s" % type(stat))
            self.cache_advantages.add(stat)
        self.save()

    def all(self):
        return self.cache_advantages

    def save(self, no_load=False):
        load_db = self.owner.storage_locations['advantages']
        self.owner.attributes.add(load_db, set(self.cache_advantages))
        if no_load:
            return
        self.load()
