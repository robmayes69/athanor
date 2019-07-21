import evennia
from django.conf import settings
from evennia.utils.utils import class_from_module

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdZone(COMMAND_DEFAULT_CLASS):
    """

    """
    key = "+zone"
    help_category = "Building"
    locks = "cmd:perm(Admin)"
    switch_options = ('create', 'rename', 'delete', 'move', 'set', 'lock', 'select')

    def switch_main(self):
        pass

    def switch_create(self):
        if '/' in self.lhs:
            dists = self.lhs.split('/')
            final = dists.pop()
            start_zone = evennia.GLOBAL_SCRIPTS.zone.search(looker=self.account, search_text='/'.join(dists))
        else:
            start_zone = evennia.GLOBAL_SCRIPTS.zone
            final = self.lhs
        new_zone = start_zone.create_child(creator=self.account, name=final)

    def switch_rename(self):
        zone = evennia.GLOBAL_SCRIPTS.zone.search(looker=self.account, search_text=self.lhs)

    def switch_delete(self):
        zone = evennia.GLOBAL_SCRIPTS.zone.search(looker=self.account, search_text=self.lhs)

    def switch_move(self):
        zone = evennia.GLOBAL_SCRIPTS.zone.search(looker=self.account, search_text=self.lhs)

    def switch_set(self):
        zone = evennia.GLOBAL_SCRIPTS.zone.search(looker=self.account, search_text=self.lhs)

    def switch_lock(self):
        zone = evennia.GLOBAL_SCRIPTS.zone.search(looker=self.account, search_text=self.lhs)

    def switch_select(self):
        zone = evennia.GLOBAL_SCRIPTS.zone.search(looker=self.account, search_text=self.lhs)