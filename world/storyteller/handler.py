from evennia.utils.utils import lazy_property



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
        return TemplateHandler(self)

    @lazy_property
    def stats(self):
        return StatHandler(self)

    @lazy_property
    def customs(self):
        return CustomHandler(self)

    @lazy_property
    def merits(self):
        return MeritHandler(self)

    @lazy_property
    def advantages(self):
        return AdvantageHandler(self)

    @lazy_property
    def pools(self):
        return PoolHandler(self)

    def save(self):
        for topic in [self.template, self.stats, self.customs, self.merits, self.advantages, self.pools]:
            topic.save()