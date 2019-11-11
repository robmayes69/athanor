from evennia.objects.objects import DefaultCharacter
from utils.events import EventEmitter


class AthanorCharacter(DefaultCharacter, EventEmitter):

    def __init__(self, *args, **kwargs):
        DefaultCharacter.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class AthanorPlayerCharacter(AthanorCharacter):
    pass


class AthanorMobileCharacter(AthanorCharacter):
    pass
