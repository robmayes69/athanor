from django.db import models
from evennia.abstracts.entity_base import TypedObject


class ChannelCategoryDB(TypedObject):
    __settingclasspath__ = "features.channels.channels.DefaultChannelCategory"
    __defaultclasspath__ = "features.channels.channels.DefaultChannelCategory"
    __applabel__ = "athcomms"

    db_channel_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='channels', on_delete=models.PROTECT)
    db_subscription_typeclass = models.ForeignKey('core.TypeclassMap', null=True, related_name='channels',
                                             on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'ChannelCategory'
        verbose_name_plural = 'ChannelCategories'


class ChannelDB(TypedObject):
    __settingclasspath__ = "features.channels.channels.DefaultChannel"
    __defaultclasspath__ = "features.channels.channels.DefaultChannel"
    __applabel__ = "athcomms"

    db_category = models.ForeignKey(ChannelCategoryDB, related_name='channel_links', null=False, on_delete=models.PROTECT)
    db_keep_log = models.BooleanField(default=False, null=False)

    class Meta:
        unique_together = (('db_key', 'db_category'),)
        verbose_name = 'Channel'
        verbose_name_plural = 'Channel'


class SubscriptionDB(TypedObject):
    __settingclasspath__ = "features.channels.channels.DefaultSubscription"
    __defaultclasspath__ = "features.channels.channels.DefaultSubscription"
    __applabel__ = "athcomms"

    db_character = models.ForeignKey('actors.ObjectDB', related_name='channel_subs', null=False, on_delete=models.CASCADE)
    db_channel = models.ForeignKey(ChannelDB, related_name='subscriptions', null=False, on_delete=models.CASCADE)
    db_voice = models.CharField(max_length=255, null=True, blank=True)
    db_codename = models.CharField(max_length=255, null=True, blank=True)
    db_gagged = models.BooleanField(default=False, null=False)
    db_enabled = models.BooleanField(default=True, null=False)

    class Meta:
        unique_together = (('db_character', 'db_channel'), ('db_character', 'db_key'), ('db_channel', 'db_codename'),)
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'