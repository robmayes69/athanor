from evennia.accounts.accounts import DefaultAccount, DefaultGuest
from . base import AthanorEntity


class AthanorAccount(DefaultAccount, AthanorEntity):

    def __init__(self, *args, **kwargs):
        DefaultAccount.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)

    def msg(self, text=None, **kwargs):
        if not text:
            return

        # Admin alert system.
        admin_alert = kwargs.pop('admin_alert', None)
        if admin_alert:
            admin_enactor = kwargs.pop('admin_enactor', None)
            text = f"|rAdmin Alert:|n |w[{admin_enactor.key}]|n {admin_alert.upper()}: {text}"

        # System Msg System
        system_alert = kwargs.pop('system_alert', None)
        if system_alert:
            sysmsg_border = self.options.sys_msg_border
            sysmsg_text = self.options.sys_msg_text
            text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_alert.upper()}|n|{sysmsg_border}>=-|n {text}"

        super(AthanorAccount, self).msg(text, **kwargs)

    def display_time(self, time_disp=None, time_format=None, tz=None):
        if not time_format:
            time_format = '%b %d %I:%M%p %Z'
        if not time_disp:
            import datetime
            time_disp = datetime.datetime.utcnow()
        if not tz:
            tz = self.options.timezone
        time = time_disp.astimezone(tz)
        return time.strftime(time_format)

    def __str__(self):
        return self.key


class AthanorGuest(DefaultGuest, AthanorAccount):
    pass
