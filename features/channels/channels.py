from . models import ChannelCategoryDB, ChannelDB, SubscriptionDB
from features.core.base import AthanorTypeEntity
from evennia.abstracts.entity_base import TypeclassBase
from typeclasses.scripts import GlobalScript


class DefaultChannelCategory(ChannelCategoryDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        ChannelCategoryDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultAthChannel(ChannelDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        ChannelDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultSubscription(SubscriptionDB, AthanorTypeEntity, metaclass=TypeclassBase):

    def __init__(self, *args, **kwargs):
        SubscriptionDB.__init__(self, *args, **kwargs)
        AthanorTypeEntity.__init__(self, *args, **kwargs)


class DefaultChannelController(GlobalScript):
    system_name = 'CHANNEL'
