from evennia.typeclasses.models import TypeclassBase
from . models import MarketDB, MarketBranchDB, MarketListingDB
from evennia.typeclasses.managers import TypeclassManager


class DefaultMarket(MarketDB, metaclass=TypeclassBase):
    objects = TypeclassManager()


class DefaultMarketBranch(MarketBranchDB, metaclass=TypeclassBase):
    objects = TypeclassManager()


class DefaultMarketListing(MarketListingDB, metaclass=TypeclassBase):
    objects = TypeclassManager()
