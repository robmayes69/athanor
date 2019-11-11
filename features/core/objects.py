from evennia.objects.objects import DefaultCharacter, DefaultExit, DefaultObject, DefaultRoom
from utils.events import EventEmitter


class AthanorCharacter(DefaultCharacter, EventEmitter):

    def __init__(self, *args, **kwargs):
        DefaultCharacter.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class AthanorExit(DefaultExit, EventEmitter):

    def __init__(self, *args, **kwargs):
        DefaultExit.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class AthanorItem(DefaultObject, EventEmitter):

    def __init__(self, *args, **kwargs):
        DefaultObject.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)


class AthanorRoom(DefaultRoom, EventEmitter):

    def __init__(self, *args, **kwargs):
        DefaultRoom.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)
