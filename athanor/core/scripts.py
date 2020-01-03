from evennia import DefaultScript
from evennia.utils.optionhandler import OptionHandler
from evennia.utils.utils import lazy_property
from athanor.utils.online import admin_accounts
from athanor.core.submessage import SubMessageMixin


class AthanorScript(DefaultScript, SubMessageMixin):
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

    def alert(self, message, enactor=None):
        for acc in admin_accounts():
            acc.system_msg(message, system_name=self.system_name, enactor=enactor)

    def msg_target(self, message, target):
        target.msg(message, system_alert=self.system_name)
