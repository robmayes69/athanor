from evennia import GLOBAL_SCRIPTS
from django.conf import settings
from evennia.utils.utils import class_from_module

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdZone(COMMAND_DEFAULT_CLASS):
    """

    """
    key = "@zone"
    help_category = "Building"
    locks = "cmd:perm(Admin)"
    switch_options = ('create', 'rename', 'delete', 'move', 'set', 'lock', 'select')

    def func(self):
        if self.switches:
            if len(self.switches) > 1:
                self.msg(f"{self.key} does not support multiple switches.")
                return
            return getattr(self, f'switch_{self.switches[0]}')()

        self.list_zones()

    def find_zone(self, search):
        manager = GLOBAL_SCRIPTS.zone
        return manager.find

    def list_zones(self):
        pass

    def switch_create(self):
        pass

    def switch_rename(self):
        pass

    def switch_delete(self):
        pass

    def switch_move(self):
        pass

    def switch_set(self):
        pass

    def switch_lock(self):
        pass

    def switch_select(self):
        pass