from django.db import models
from evennia.typeclasses.models import TypedObject
from evennia.typeclasses.managers import TypeclassManager


class MarketDB(TypedObject):
    __settingclasspath__ = "features.market.market.DefaultMarket"
    __defaultclasspath__ = "features.market.market.DefaultMarket"
    __applabel__ = "market"
    objects = TypeclassManager()

    db_description = models.TextField(null=True)

    class Meta:
        verbose_name = 'Market'
        verbose_name_plural = 'Market'


class MarketBranchDB(TypedObject):
    __settingclasspath__ = "features.market.market.DefaultMarketBranch"
    __defaultclasspath__ = "features.market.market.DefaultMarketBranch"
    __applabel__ = "market"
    objects = TypeclassManager()

    db_owner = models.ForeignKey('objects.ObjectDB', related_name='managed_markets', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'MarketBranch'
        verbose_name_plural = 'MarketBranches'


class MarketListingDB(TypedObject):
    __settingclasspath__ = "features.market.market.DefaultMarketListing"
    __defaultclasspath__ = "features.market.market.DefaultMarketListing"
    __applabel__ = "market"
    objects = TypeclassManager()

    db_branch = models.ForeignKey(MarketBranchDB, related_name='market_listings', on_delete=models.PROTECT)
    db_item = models.ForeignKey('objects.ObjectDB', related_name='market_sale_listings', on_delete=models.CASCADE, unique=True)
    db_owner = models.ForeignKey('objects.ObjectDB', related_name='market_sales', on_delete=models.PROTECT)
    db_price_per_unit = models.FloatField(default=0, null=False)