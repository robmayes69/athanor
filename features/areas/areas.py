from evennia.typeclasses.models import TypeclassBase
from features.areas.models import AreaDB
from typeclasses.scripts import GlobalScript
from utils.events import EventEmitter

class DefaultAreaManager(GlobalScript):
    system_name = 'AREA'
    option_dict = {
        'area_locks': (
        'Default locks to use for new Areas', 'Lock', 'see:all()')
    }


class DefaultArea(AreaDB, EventEmitter, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        AreaDB.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)

