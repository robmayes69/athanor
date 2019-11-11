from evennia.objects.objects import DefaultExit
from utils.events import EventEmitter


class AthanorExit(DefaultExit, EventEmitter):

    def __init__(self, *args, **kwargs):
        DefaultExit.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)
