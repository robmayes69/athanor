from evennia.utils.events import EventEmitter


class BaseStat(EventEmitter):
    name = None

    def __init__(self, handler):
        EventEmitter.__init__(self)
        self.handler = handler


class StatHandler(object):

    def __init__(self, actor):
        self.actor = actor
