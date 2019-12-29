class BaseMaster(object):

    def __init__(self, world, extension, category, master_key, actor_class, master_data):
        self.world = world
        self.extension = extension
        self.category = category
        self.unique_key = master_key
        self.actor_class = actor_class
        self.master_data = master_data

    def create(self, actor_id, model=None, actor_data=None):
        return self.actor_class(self, actor_id, model, actor_data)
