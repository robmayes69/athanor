from future.utils import with_metaclass
from evennia.typeclasses.models import TypeclassBase
from features.areas.models import AreaDB


class DefaultArea(with_metaclass(TypeclassBase, AreaDB)):
    pass