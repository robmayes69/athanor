from commands.library import AthanorError, sanitize_string, partial_match, dramatic_capitalize
from evennia.utils.ansi import ANSIString

class Merit(object):

    __slots__ = ['base_name', 'main_category', '_context', '_value', '_description', 'game_category']

    base_name = 'Merit'
    game_category = 'Storyteller'
    main_category = 'Merit'
    _name = None
    _context = None
    _value = 0
    _description = None

    def __init__(self, name=None, context=None, value=None):
        if not name:
            raise AthanorError("A %s requires a name!" % self.base_name)
        self.current_name = name
        if context:
            self.current_context = context
        if value:
            self.current_value = value

    def __unicode__(self):
        return unicode(self.full_name)

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return '<%s: %s - (%s)>' % (self.main_category, self.full_name, self.current_value)

    def __nonzero__(self):
        return True

    def __int__(self):
        return self.current_value

    def __eq__(self, other):
        return (type(self) == type(other)) and (self.full_name == other.full_name)

    def __hash__(self):
        return self.base_name.__hash__() + self.full_name.lower().__hash__()

    def __add__(self, other):
        return int(self) + int(other)

    def __radd__(self, other):
        return int(self) + int(other)

    @property
    def full_name(self):
        if self._context:
            return '%s: %s' % (self._name, self._context)
        return self._name

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
    def current_name(self):
        return self._name

    @current_name.setter
    def current_name(self, value):
        if value == '' or value == None:
            self._name = None
        else:
            self._name = dramatic_capitalize(sanitize_string(str(value), strip_mxp=True, strip_ansi=True))

    @property
    def current_description(self):
        return self._description

    @current_description.setter
    def current_description(self, value):
        if value == '' or value == None:
            self._description = None
        else:
            self._description = sanitize_string(str(value), strip_mxp=True)

    @property
    def current_context(self):
        return self._context

    @current_context.setter
    def current_context(self, value):
        if value == '' or value == None:
            self._context = None
        else:
            self._context = dramatic_capitalize(sanitize_string(str(value), strip_mxp=True))

    def sheet_format(self, width=36, fill_char='.', colors={'statname': 'n', 'statfill': 'n', 'statdot': 'n'}):
        display_name = ANSIString('{%s%s{n' % (colors['statname'], self.full_name))
        if self.current_value > width - len(display_name) - 1:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], self.current_value))
        else:
            dot_display = ANSIString('{%s%s{n' % (colors['statdot'], '*' * self.current_value))
        fill_length = width - len(display_name) - len(dot_display)
        fill = ANSIString('{%s%s{n' % (colors['statfill'], fill_char * fill_length))
        return display_name + fill + dot_display

class MeritHandler(object):

    __slots__ = ['owner', 'cache_merits']

    def __init__(self, owner):
        self.owner = owner
        self.cache_merits = list()
        self.load()

    def load(self):
        load_db = self.owner.storage_locations['merits']
        load_merits = list(set(self.owner.attributes.get(load_db, [])))
        load_merits = [merit for merit in load_merits if isinstance(merit, Merit)]
        self.cache_merits = load_merits

    def save(self, no_load=False):
        load_db = self.owner.storage_locations['merits']
        self.owner.attributes.add(load_db, self.cache_merits)
        if no_load:
            return
        self.load()

    def all(self):
        return self.cache_merits

    def add(self, merit_type=None, name=None, value=None, caller=None):
        if not caller:
            caller = self.owner
        if not merit_type:
            raise AthanorError("Must enter a specific type!")
        if not name:
            raise AthanorError("Must enter a name!")
        if not value:
            raise AthanorError("Must enter a rank!")
        if not isinstance(merit_type, Merit):
            found_type = partial_match(merit_type, self.types_dict.keys())
            if not found_type:
                raise AthanorError('Type not found.')
            merit_type = self.types_dict[found_type]
        if ':' in name:
            name, context = name.split(':', 1)
            context = context.strip()
        else:
            context = None
        new_merit = merit_type(name=name, context=context, value=value)
        if new_merit in self.cache_merits:
            raise AthanorError("A %s of that name and context already exists." % merit_type.base_name)
        self.cache_merits.add(new_merit)
        self.save()
        caller.sys_msg('Added a new %s: %s (%s)' % (merit_type.base_name, new_merit, int(new_merit)))

    def describe(self, merit_type=None, name=None, value=None, caller=None):
        if not caller:
            caller = self.owner
        if not merit_type:
            raise AthanorError("Must enter a specific type!")
        if not name:
            raise AthanorError("Must enter a specific type!")
        if value == None:
            raise AthanorError("Must enter a description!")
        found_type = partial_match(merit_type, self.merits_dict.keys())
        if not found_type:
                raise AthanorError('Type not found.')
        search_merits = self.merits_dict[found_type]
        found_merit = partial_match(name, search_merits)
        if not found_merit:
            raise AthanorError("No %s called '%s' could be found." % (found_type.base_name, name))
        found_merit.current_description = value
        self.save()
        return True