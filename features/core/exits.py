from evennia.objects.objects import DefaultExit
from features.core.base import AthanorEntity


class AthanorExit(DefaultExit, AthanorEntity):

    def __init__(self, *args, **kwargs):
        DefaultExit.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)
