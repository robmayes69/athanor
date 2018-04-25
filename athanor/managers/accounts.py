from athanor.managers.base import __BaseManager


class AccountManager(__BaseManager):
    mode = 'account'

    def at_account_creation(self):
        for handler in self.ordered_handlers:
            handler.at_account_creation()

    def at_post_login(self, session, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_post_login(session, **kwargs)

    def at_true_login(self, session, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_true_login(session, **kwargs)

    def at_failed_login(self, session, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_failed_login(session, **kwargs)

    def at_init(self):
        for handler in self.ordered_handlers:
            handler.at_init()

    def at_disconnect(self, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_disconnect(**kwargs)

    def at_true_logout(self, **kwargs):
        for handler in self.ordered_handlers:
            handler.at_true_logout(**kwargs)

    def render_login(self, session, viewer):
        message = []
        for handler in self.ordered_handlers:
            message.append(handler.render_login(session, viewer))
        return '\n'.join([unicode(line) for line in message if line])