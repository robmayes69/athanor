from evennia import DefaultChannel
from utils.events import EventEmitter


class AthanorChannel(DefaultChannel, EventEmitter):

    def __init__(self, *args, **kwargs):
        DefaultChannel.__init__(self, *args, **kwargs)
        EventEmitter.__init__(self, *args, **kwargs)