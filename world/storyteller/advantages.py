class AdvantageHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.load()
        self.save(no_load=True)

    def load(self):
        pass

    def save(self, no_load=False):
        pass