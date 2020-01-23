from django.conf import settings

from evennia import DefaultScript
from evennia.utils.optionhandler import OptionHandler
from evennia.utils.utils import lazy_property, class_from_module

from athanor.utils.online import admin_accounts
from athanor.utils.events import EventEmitter

MIXINS = [class_from_module(mixin) for mixin in settings.MIXINS["SCRIPT"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorScript(*MIXINS, DefaultScript, EventEmitter):
    pass


class AthanorOptionScript(AthanorScript):
    option_dict = dict()

    @lazy_property
    def options(self):
        return OptionHandler(self,
                             options_dict=self.option_dict,
                             savefunc=self.attributes.add,
                             loadfunc=self.attributes.get,
                             save_kwargs={"category": 'option'},
                             load_kwargs={"category": 'option'})


class AthanorGlobalScript(AthanorOptionScript):
    system_name = 'SYSTEM'

    @lazy_property
    def loaded(self):
        """
        This lazy property is provided as a fail-safe to ensure that a Global Script
        never 'loads' twice.
        """
        return False

    def alert(self, message, enactor=None):
        for acc in admin_accounts():
            acc.system_msg(message, system_name=self.system_name, enactor=enactor)

    def msg_target(self, message, target):
        target.msg(message, system_alert=self.system_name)

    def load(self):
        if self.loaded:
           return
        self.at_load()
        self.loaded = True

    def at_load(self):
        """
        Implements the actual logic of loading. Meant to be overloaded.
        """
        pass
