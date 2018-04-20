import importlib
from django.conf import settings
from evennia import create_script

class AllConfigManager(object):
    """
    Singleton that loads when module is called.

    Grab it via ATHANOR_MANAGERS.
    """

    def __init__(self):
        self.configs_list = list()
        self.configs = dict()

        for conf in settings.ATHANOR_CONFIG:
            module = importlib.import_module(conf)
            self.configs_list += module.ALL
        self.configs_classes = {con.key: con for con in self.configs_list}
        self.load()

    def load(self):
        for key in self.configs_classes.keys():
            self[key]

    def __getitem__(self, item):
        if item in self.configs:
            return self.configs[item]
        if item not in self.configs_classes:
            raise ImportError("Athanor Config Manager: cannot import '%s'" % item)
        cls = self.configs_classes[item]
        found = cls.objects.filter_family(db_key=cls.key).first()
        if found:
            self.configs[item] = found
            return found
        config = create_script(cls, persistent=True, obj=None)
        self.configs[item] = config
        return config


ALL_MANAGERS = dict()


def GET_MANAGERS():
    if not 'manager' in ALL_MANAGERS:
        ALL_MANAGERS['manager'] = AllConfigManager()
    return ALL_MANAGERS['manager']