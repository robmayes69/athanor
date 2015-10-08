from commands.library import AthanorError
from evennia.utils.utils import make_iter

class Stat(object):

    __slots__ = ['base_name', 'game_category', 'sub_category', 'can_multiple', 'can_context', 'can_favor',
                 'can_supernal', 'can_specialize', 'can_roll', 'can_bonus', 'max_context_length',
                 'current_bonus', 'current_rank', 'current_favored', 'current_supernal']

    base_name = 'DefaultStat'
    game_category = None
    sub_category = None
    can_multiple = False
    can_context = False
    can_favor = False
    can_supernal = False
    can_specialize = False
    can_roll = False
    can_bonus = False
    can_multiple_rank = False
    max_context_length = 80
    current_bonus = 0
    current_context = None
    current_rank = None
    current_favored = False
    current_supernal = False

    def __unicode__(self):
        return unicode(self.full_name)

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return '<%s: %s - (%s)>' % (self.game_category, self.full_name, self.display_rank)

    def __nonzero__(self):
        return True

    def __int__(self):
        return self.roll_value

    def __eq__(self, other):
        return type(self) == type(other)

    @property
    def full_name(self):
        if self.current_context:
            return '%s: %s' % (self.base_name, self.current_context)
        else:
            return self.base_name

    @property
    def display_rank(self):
        if self.can_multiple_rank:
            return ", ".join([str(rank) for rank in self.current_rank])
        else:
            return str(self.current_rank or 0)

    @property
    def roll_value(self):
        return (self.natural_rank + self.bonus_rank) or 0

    @property
    def natural_rank(self):
        return max(make_iter(self.current_rank))

    @property
    def bonus_rank(self):
        return self.current_bonus