from evennia.accounts.accounts import DefaultAccount, DefaultGuest
from features.core.base import AthanorEntity
from typeclasses.scripts import GlobalScript


class AthanorAccount(DefaultAccount, AthanorEntity):

    def __init__(self, *args, **kwargs):
        DefaultAccount.__init__(self, *args, **kwargs)
        AthanorEntity.__init__(self, *args, **kwargs)

    def system_msg(self, text=None, system_name=None, enactor=None):
        sysmsg_border = self.options.sys_msg_border
        sysmsg_text = self.options.sys_msg_text
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

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


class DefaultAccountController(GlobalScript):
    system_name = 'ACCOUNTS'

    def at_start(self):
        pass

    def create_account(self, session, username, email, password):
        pass

    def rename_account(self, session, account, new_name):
        pass

    def change_email(self, session, account, new_email):
        pass

    def find_account(self, search_text):
        if isinstance(search_text, AthanorAccount):
            return search_text

    def disable_account(self, session, account):
        pass

    def enable_account(self, session, account):
        pass

    def ban_account(self, session, account, duration):
        pass

