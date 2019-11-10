from django.dispatch import Signal


class EventManager(object):

    def __init__(self):
        self.events = dict()

    def get_event(self, event):
        if event not in self.events.keys():
            self.events[event] = Signal()
        return self.events[event]

    def on(self, obj, event, callback):
        sig = self.get_event(event)
        return sig.connect(callback)

    def emit(self, obj, event, **kwargs):
        sig = self.get_event(event)
        results = sig.send(obj, **kwargs)
        return tuple([(r[0].__self__, r[1]) for r in results if r[0]])


EVENT_MANAGER = EventManager()


class EventEmitter(object):
    _global_event_manager = EVENT_MANAGER

    def __init__(self, *args, **kwargs):
        self._local_event_manager = EventManager()

    def on_global(self, event, callback):
        return self._global_event_manager.on(self, event, callback)

    def test_global(self, event, **kwargs):
        self.emit_global(event, **kwargs)

    def emit_global(self, event, **kwargs):
        return self._global_event_manager.emit(self, event, **kwargs)

    def on_local(self, event, callback):
        return self._local_event_manager.on(self, event, callback)

    def emit_local(self, event, **kwargs):
        return self._local_event_manager.emit(self, event, **kwargs)
