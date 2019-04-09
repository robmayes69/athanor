class StatNode(object):
    key = None
    parent_key = None
    children = list()
    category = None
    tags = set()
    description = None
    parent_class = None
    sort_order = 0

    def __init__(self, handler):
        self.handler = handler
        self.owner = handler.owner
        self.load()

    def load(self):
        pass

    def save(self):
        data = self.export()
        self.handler.add(self.key, value=data)

    def export(self):
        return ''
