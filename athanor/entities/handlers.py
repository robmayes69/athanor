from evennia.objects.objects import ObjectSessionHandler


class KeywordHandler(object):

    def __init__(self, owner):
        self.owner = owner

    def all(self, looker=None):
        pass