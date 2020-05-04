from athanor.utils.cmdhandler import CmdHandler
from athanor.utils.cmdsethandler import CmdSetHandler


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


class EntityEquipHandler:

    def __init__(self, owner):
        self.owner = owner


class EntityInventoryHandler:

    def __init__(self, owner):
        self.owner = owner
