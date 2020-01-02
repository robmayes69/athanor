from evennia.objects.objects import DefaultExit
from athanor.core.gameentity import AthanorGameEntity


class AthanorExit(DefaultExit, AthanorGameEntity):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
