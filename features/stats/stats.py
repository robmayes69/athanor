from evennia.typeclasses.models import TypeclassBase
from . models import StatCategoryDB, StatDB


class DefaultStatCategory(StatCategoryDB, metaclass=TypeclassBase):
    pass


class DefaultStat(StatDB, metaclass=TypeclassBase):
    pass
