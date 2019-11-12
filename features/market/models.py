from django.db import models
from evennia.typeclasses.models import TypedObject


class MarketDB(TypedObject):
    __settingclasspath__ = "features.market.market.DefaultMarket"
    __defaultclasspath__ = "features.market.market.DefaultMarket"
    __applabel__ = "market"

    db_description = models.TextField(null=True)
    db_branch_typeclass = models.ForeignKey('core.TypeclassMap', null=True, on_delete=models.PROTECT)
    db_listing_typeclass = models.ForeignKey('core.TypeclassMap', null=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Market'
        verbose_name_plural = 'Market'


class MarketBranchDB(TypedObject):
    __settingclasspath__ = "features.market.market.DefaultMarketBranch"
    __defaultclasspath__ = "features.market.market.DefaultMarketBranch"
    __applabel__ = "market"

    db_market = models.ForeignKey(MarketDB, related_name='branches', on_delete=models.PROTECT)
    db_entity = models.ForeignKey('core.EntityMapDB', related_name='market_branches', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'MarketBranch'
        verbose_name_plural = 'MarketBranches'


class MarketListingDB(TypedObject):
    __settingclasspath__ = "features.market.market.DefaultMarketListing"
    __defaultclasspath__ = "features.market.market.DefaultMarketListing"
    __applabel__ = "market"

    db_branch = models.ForeignKey(MarketBranchDB, related_name='market_listings', on_delete=models.PROTECT)
    db_item = models.ForeignKey('objects.ObjectDB', related_name='market_sale_listings', on_delete=models.CASCADE, unique=True)
    db_owner = models.ForeignKey('core.EntityMapDB', related_name='market_sales', on_delete=models.PROTECT)
    db_price_per_unit = models.FloatField(default=0.0, null=False)

    class Meta:
        verbose_name = 'MarketListing'
        verbose_name_plural = 'MarketListings'
