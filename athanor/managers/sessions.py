from athanor.managers.base import __BaseManager

class SessionManager(__BaseManager):
    mode = 'session'
    handlers_mode = 'HANDLERS_SESSION'

    def at_sync(self):
        for handler in self.ordered_handlers:
            handler.at_sync()

    def at_login(self, account, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_login(account, **kwargs)

    def at_disconnect(self, reason, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_disconnect(reason, **kwargs)