from evennia.objects.objects import ObjectSessionHandler


class KeywordHandler(object):

    def __init__(self, owner):
        self.owner = owner

    def all(self, looker=None):
        pass


class FormHandler(object):

    @property
    def persistent(self):
        return self.owner.persistent

    def __init__(self, owner):
        self.owner = owner
        self.forms = dict()
        self.active = None
