from evennia import GLOBAL_SCRIPTS
from django.conf import settings
from evennia.utils.utils import class_from_module

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdArea(COMMAND_DEFAULT_CLASS):
    """

    """
    key = "@area"
    help_category = "Building"
    locks = "cmd:perm(Admin)"
    switch_options = ['create', 'rename', 'delete', 'move', 'set', 'lock', 'select', 'owner', 'roomtypeclass',
                      'exittypeclass']

    def switch_main(self):
        if self.args:
            return self.switch_display()

    def switch_create(self):
        area_parent = None
        if '/' in self.lhs:
            area_parent = self.lhs.split('/')
            create_name = area_parent.pop().strip()
            area_parent = '/'.join(area_parent)
        else:
            create_name = self.lhs
        GLOBAL_SCRIPTS.areas.create_area(self.session, create_name, area_parent)

    def switch_rename(self):
        GLOBAL_SCRIPTS.areas.rename_area(self.session, self.lhs, self.rhs)

    def switch_delete(self):
        GLOBAL_SCRIPTS.areas.delete_area(self.session, self.lhs, self.rhs)

    def switch_move(self):
        GLOBAL_SCRIPTS.areas.search(self.session, self.lhs, self.rhs)

    def switch_set(self):
        GLOBAL_SCRIPTS.areas.search(looker=self.account, search_text=self.lhs)

    def switch_lock(self):
        GLOBAL_SCRIPTS.areas.search(looker=self.account, search_text=self.lhs)

    def switch_select(self):
        GLOBAL_SCRIPTS.areas.search(looker=self.account, search_text=self.lhs)

    def switch_roomtypeclass(self):
        pass

    def switch_owner(self):
        pass

    def switch_exittypeclass(self):
        pass