from evennia.utils import lazy_property
from athanor.handlers.base import ScriptHandler as oldBase
from athanor.classes.scripts import AthanorScript


class ConfigManagerScript(AthanorScript):
    key = 'base'
    manager = None

    @lazy_property
    def settings(self):
        return self.manager(self)

    def __getitem__(self, item):
        return self.settings[item]


class ConfigManager(oldBase):
    pass