from . species import SPECIES_DICT


class BaseManager(object):

    def __init__(self, owner, classes):
        self.owner = owner
        self.attr = owner.attributes
        self.input_classes = classes
        self.hooks = dict()
        self.classes = list()
        self.handlers_list = list()
        self.handlers = dict()

    def used_handlers(self):
        return self.input_classes

    def reload(self):
        self.classes = sorted(self.used_handlers(), key=lambda c: c.priority)
        self.handlers_list = [c(self) for c in self.classes]
        self.handlers = {c.key: c for c in self.handlers_list}
        for c in self.handlers_list:
            c.load_finish()

    def register(self, hook, handler):
        if hook not in self.hooks:
            self.hooks[hook] = set()
        self.hooks[hook].add(handler)

    def call_hook(self, hook, *args, **kwargs):
        if hook not in self.hooks:
            return
        for h in self.hooks[hook]:
            getattr(h, 'hook_on_%s' % hook)(*args, **kwargs)

    def __getitem__(self, item):
        return self.handlers[item]


class CharacterManager(BaseManager):
    pass