import datetime
from django.conf import settings

from evennia.utils.utils import class_from_module
from evennia.accounts.accounts import DefaultAccount

from athanor.utils.events import EventEmitter

MIXINS = [class_from_module(mixin) for mixin in settings.GAMEDB_MIXINS["ACCOUNT"]]
MIXINS.sort(key=lambda x: getattr(x, "mixin_priority", 0))


class AthanorAccount(*MIXINS, DefaultAccount, EventEmitter):
    """
    AthanorAccount adds the EventEmitter to DefaultAccount and supports Mixins.
    Please read Evennia's documentation for its normal API.

    Triggers Global Events:
        account_connect (session): Fired whenever a Session authenticates to this account.
        account_disconnect (session): Triggered whenever a Session disconnects from this account.
        account_online (session): Fired whenever an account comes online from being completely offline.
        account_offline (session): Triggered when an account's final session closes.
    """

    def system_msg(self, text=None, system_name=None, enactor=None):
        sysmsg_border = self.options.sys_msg_border
        sysmsg_text = self.options.sys_msg_text
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def localize_timestring(self, time_data=None, time_format='%b %d %I:%M%p %Z', tz=None):
        if not time_data:
            time_data = datetime.datetime.utcnow()
        if not tz:
            tz = self.options.timezone
        return time_data.astimezone(tz).strftime(time_format)

    def __str__(self):
        return self.key

    @classmethod
    def create_account(cls, *args, **kwargs):
        account, errors = cls.create(*args, **kwargs)
        if account:
            return account
        else:
            raise ValueError(errors)

    def at_post_disconnect(self, **kwargs):
        super().at_post_disconnect(**kwargs)
        self.emit_global("account_disconnect")
        if not self.sessions.all():
            self.emit_global("account_offline")

    def at_post_login(self, session=None, **kwargs):
        super().at_post_login(session, **kwargs)
        self.emit_global("account_connect", session=session)
        if len(self.sessions.all()) == 1:
            self.emit_global("account_online", session=session)
