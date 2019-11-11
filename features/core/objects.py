from evennia.objects.objects import DefaultObject
from utils.events import EventEmitter


class AthanorObject(DefaultObject, EventEmitter):

    def __init__(self, *args, **kwargs):
        DefaultObject.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)
