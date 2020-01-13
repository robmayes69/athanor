class AspectHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self.aspects = dict()

    def all(self):
        return self.aspects.values()
