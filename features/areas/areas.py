from evennia.typeclasses.models import TypeclassBase
from features.areas.models import AreaDB
from typeclasses.scripts import GlobalScript


class DefaultAreaManager(GlobalScript):
    system_name = 'AREA'
    option_dict = {
        'area_locks': (
        'Default locks to use for new Areas', 'Lock', 'see:all()')
    }


class DefaultArea(AreaDB, metaclass=TypeclassBase):
    pass
