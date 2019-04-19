class BaseHandler(object):
    interface = dict()
    priority = 0
    key = None
    attributes = dict()

    def __init__(self, manager):
        self.manager = manager
        self.owner = manager.owner
        self.attr = manager.owner.attributes
        self.register()
        self.integrity_check()
        self.load()
        self.save()

    def register(self):
        pass

    def save(self):
        pass

    def load(self):
        pass

    def integrity_check(self):
        for k, v in self.attributes.items():
            if not self.attr.has(k) or not isinstance(self.attr.get(k), type(v)):
                self.attr.add(k, v)
