from athanor.utils.cmdhandler import CmdHandler
from athanor.utils.cmdsethandler import CmdSetHandler
from athanor.equips.utils import EquipHandler
from athanor.inventories.utils import InventoryHandler


class LocationHandler:

    def __init__(self, owner):
        self.owner = owner

    def set_sector(self, sector, coordinates, force=False):
        pass

    def set_room(self, room, force=False):
        pass


class EntityCmdSetHandler(CmdSetHandler):
    pass


class EntityCmdHandler(CmdHandler):
    pass


class EntityEquipHandler(EquipHandler):

    def __init__(self, owner):
        self.owner = owner


class EntityInventoryHandler(InventoryHandler):

    def __init__(self, owner):
        self.owner = owner
