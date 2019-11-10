from evennia.typeclasses.models import TypeclassBase
from . models import MarketDB, MarketBranchDB, MarketListingDB


class DefaultMarket(MarketDB, metaclass=TypeclassBase):
    pass


class DefaultMarketBranch(MarketBranchDB, metaclass=TypeclassBase):
    pass


class DefaultMarketListing(MarketListingDB, metaclass=TypeclassBase):
    pass
