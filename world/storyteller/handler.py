from evennia.utils.utils import lazy_property

from world.storyteller.templates import TemplateHandler
from world.storyteller.stats import StatHandler, CustomHandler
from world.storyteller.pools import PoolHandler
from world.storyteller.merits import MeritHandler
from world.storyteller.advantages import AdvantageHandler

class StorytellerHandler(object):

    def __init__(self, owner):
        self.owner = owner
        """
        template = self.template
        stats = self.stats
        customs = self.customs
        merits = self.merits
        advantages = self.advantages
        pools = self.pools
        """

    @lazy_property
    def template(self):
        return TemplateHandler(self.owner)

    @lazy_property
    def stats(self):
        return StatHandler(self.owner)

    @lazy_property
    def customs(self):
        return CustomHandler(self.owner)

    @lazy_property
    def merits(self):
        return MeritHandler(self.owner)

    @lazy_property
    def advantages(self):
        return AdvantageHandler(self.owner)

    @lazy_property
    def pools(self):
        return PoolHandler(self.owner)

    def save(self):
        for topic in [self.template, self.stats, self.customs, self.merits, self.advantages, self.pools]:
            topic.save()