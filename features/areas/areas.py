from evennia.typeclasses.models import TypeclassBase
from features.areas.models import AreaDB
from typeclasses.scripts import GlobalScript
from features.core.base import AthanorTypeEntity

class DefaultAreaController(GlobalScript):
    system_name = 'AREA'
    option_dict = {
        'area_locks': (
        'Default locks to use for new Areas', 'Lock', 'see:all()')
    }


class DefaultArea(AreaDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        AreaDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)

