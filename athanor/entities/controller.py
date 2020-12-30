from athanor.utils.controllers import AthanorController, AthanorControllerBackend
from athanor.utils import error
from athanor.entities.rooms import AthanorRoom
from athanor.entities.exits import AthanorExit

from athanor.zones.zones import DefaultZone
from typing import Union, Optional


class AthanorGridController(AthanorController):
    system_name = 'GRID'

    def __init__(self, key, manager, backend):
        super().__init__(key, manager, backend)
        self.load()

    def create_room(self, session, zone: Union[str, DefaultZone], room_name: str):
        pass

    def create_exit(self, session, room: AthanorRoom, exit_dir: str, tunnel=True):
        pass


class AthanorGridControllerBackend(AthanorControllerBackend):
    typeclass_defs = [
        ('room_typeclass', 'BASE_ROOM_TYPECLASS', AthanorRoom),
        ('exit_typeclass', 'BASE_EXIT_TYPECLASS', AthanorExit)
    ]

    def __init__(self, frontend):
        super().__init__(frontend)
        self.exit_typeclass = None
        self.room_typeclass = None
        self.load()
