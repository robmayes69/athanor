from evennia import DefaultChannel
from features.core.base import AthanorEntity


class AthanorChannel(DefaultChannel, AthanorEntity):

    def __init__(self, *args, **kwargs):
        DefaultChannel.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)