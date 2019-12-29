class BaseInventory(object):

    def __init__(self, handler):
        self.handler = handler
        self.contents = set()
        self.contents_sorted = list()
        self.prototype_index = dict()
        self.weight = 0

    def add(self, item, sort_index=None):
        pass

    def remove(self, item):
        pass

    def all(self):
        return self.contents


class PersistentInventory(BaseInventory):
    pass


class InventoryHandler(object):

    def __init__(self, actor):
        self.actor = actor
        self.inventories = dict()

    def all_items(self):
        all_items = set()
        for inventory in self.inventories.values():
            all_items += inventory.all()
        return all_items