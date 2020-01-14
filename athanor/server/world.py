from django.conf import settings
from evennia.utils.utils import class_from_module
from evennia import DefaultObject


class World(object):
    """
    This is the Engine that ties together the entire game.
    """

    def __init__(self):
        self.data_manager = class_from_module(settings.GAME_DATA_MANAGER_CLASS)(self)
        self.alliances = set()
        self.alliance_keys = dict()
        self.factions = set()
        self.faction_keys = dict()
        self.load()

    def load(self):
        self.data_manager.load()

    def resolve_room_path(self, path):
        if '/' not in path:
            raise ValueError(f"Path is malformed. Must be in format of OBJ/ROOM_KEY")
        obj, room_key = path.split('/', 1)
        if obj.startswith('#'):
            obj = obj[1:]
            if obj.isdigit():
                if not (found := DefaultObject.objects.filter(id=int(obj)).first()):
                    raise ValueError(f"Cannot find an object for #{obj}!")
                if not hasattr(found, 'instance_bridge'):
                    raise ValueError(f"Must target objects with internal maps.")
            else:
                raise ValueError(f"Path is malformed. Must be in format of OBJ/ROOM_KEY")
        else:
            if not (found := self.data_manager.regions.get(obj, None)):
                raise ValueError(f"Cannot find a region for {obj}!")
        if not room_key:
            raise ValueError(f"Path is malformed. Must be in format of OBJ/ROOM_KEY")
        if not (room := found.instance.get_room(room_key)):
            raise ValueError(f"Cannot find that room_key in {found}!")
        return room