from django.conf import settings

from evennia import DefaultScript
from evennia.utils.optionhandler import OptionHandler
from evennia.utils.utils import lazy_property, class_from_module

from athanor.utils.events import EventEmitter
from athanor.gamedb.base import HasRenderExamine

MIXINS = [class_from_module(mixin) for mixin in settings.GAMEDB_MIXINS["SCRIPT"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorScript(*MIXINS, HasRenderExamine, DefaultScript, EventEmitter):
    """
    Really just a Script class that accepts the Mixin framework and supports Events.
    """
    examine_type = 'script'

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.key}>"

    def render_examine(self, viewer, callback=True):
        return self.render_examine_callback(None, viewer, callback=callback)


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
