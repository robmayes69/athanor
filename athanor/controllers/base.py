from django.conf import settings


from evennia.utils.utils import class_from_module

from athanor.utils.online import admin_accounts
from athanor.utils.events import EventEmitter

MANAGER_MIXINS = [class_from_module(mixin) for mixin in settings.CONTROLLER_MIXINS["CONTROLLER_MANAGER"]]
MANAGER_MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))

BASE_MIXINS = [class_from_module(mixin) for mixin in settings.CONTROLLER_MIXINS["BASE_CONTROLLER"]]
BASE_MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class ControllerManager(*MANAGER_MIXINS, EventEmitter):

    def __init__(self):
        self.loaded = False
        self.controllers = dict()

    def load(self):
        for controller_key, controller_def in settings.CONTROLLERS.items():
            con_class = class_from_module(controller_def.get("class", settings.BASE_CONTROLLER_CLASS))
            self.controllers[controller_key] = con_class(controller_key, self)
        self.loaded = True

    def get(self, con_key):
        if not self.loaded:
            self.load()
        if not (found := self.controllers.get(con_key, None)):
            raise ValueError("Controller not found!")
        if not found.loaded:
            found.load()
        return found


class AthanorController(*BASE_MIXINS, EventEmitter):
    system_name = 'SYSTEM'

    def __init__(self, key, manager):
        self.key = key
        self.manager = manager
        self.loaded = False

    def alert(self, message, enactor=None):
        for acc in admin_accounts():
            acc.system_msg(message, system_name=self.system_name, enactor=enactor)

    def msg_target(self, message, target):
        target.msg(message, system_alert=self.system_name)

    def load(self):
        """
        This is a wrapper around do_load that prevents it from being called twice.

        Returns:
            None
        """
        if self.loaded:
            return
        self.do_load()
        self.loaded = True

    def do_load(self):
        """
        Implements the actual logic of loading. Meant to be overloaded.
        """
        pass
