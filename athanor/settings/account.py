from athanor.settings.base import TimeZoneSetting, FutureSetting, UnsignedIntegerSetting, BoolSetting
from athanor.utils.time import utcnow


class BannedUntil(FutureSetting):
    key = 'banned_until'
    description = 'Stores Timestamp of when ban duration is up. Only valid if stored value > Now.'

    def report_change(self, resp):
        if self.loaded:
            resp.success.append("Account Banned until: ${localtime,%s}") % self.value_storage
            resp.json('success', message='Account Banned', target=self.owner, timestamp=self.value_storage)
            msg = 'Your Account has been banned Until: ${localtime,%s}' % self.value_storage
        else:
            msg = 'Your Account has been un-banned!'
            resp.success.append("Account un-banned!")
            resp.json('success', message='Account un-banned!', target=self.owner)
        self.handler.console_msg(msg)

    def report_clear(self, resp):
        msg = 'Your Account has been un-banned!'
        resp.success.append("Account un-banned!")
        resp.json('success', message='Account un-banned!', target=self.owner)
        self.handler.console_msg(msg)
    
    def post_set(self):
        if self.loaded and self.value > utcnow():
            self.owner.disconnect_all_sessions()


class ExtraCharacterSlots(UnsignedIntegerSetting):
    key = 'extra_character_slots'
    description = 'Stores number of extra character slots. This builds on settings.py. Can be negative. End result floors at 0.'
    default = 0

    def report_change(self, resp):
        resp.success.append("Extra Character Slots changed to: %s" % self.value)
        resp.json('success', message='Extra Character Slots Changed!', value=self.value)
        self.handler.console_msg("Your Extra Character Slots was changed to: %s" % self.value)

    def report_clear(self, resp):
        resp.success.append("Extra Character Slots restored to defaults.")
        resp.json('success', message='Extra Character Slots Restored to defaults!')
        self.handler.console_msg("Your Extra Character Slots was restored to defaults.")


class DisableToggle(BoolSetting):
    key = 'disabled'
    description = 'Stores data about whether the account is disabled. This supersedes Banning.'
    default = 0

    def report_change(self, resp):
        if self.value:
            msg = "Your Account has been disabled!"
            resp.success.append("Account Disabled!")
            resp.json('success', message='Account Disabled', target=self.owner)
        else:
            msg = "Your Account has been enabled!"
            resp.success.append("Account Enabled!")
            resp.json('success', message='Account Enabled!', target=self.owner)
        self.handler.console_msg(msg)
        
    def report_clear(self, resp):
        msg = "Your Account has been enabled!"
        resp.success.append("Account Enabled!")
        resp.json('success', message='Account Enabled!', target=self.owner)
        self.handler.console_msg(msg)
        
    def post_set(self):
        if self.value:
            self.owner.disconnect_all_sessions()


class Dark(BoolSetting):
    key = 'dark'
    description = 'Stores whether owner is Dark.'
    default = 0

    def report_change(self, resp):
        if self.value:
            msg = "Your Account is now Dark!"
            resp.success.append("Account turned Dark!")
            resp.json('success', "Account is now Dark!", target=self.owner)
        else:
            msg = "Your Account is no longer Dark!"
            resp.success.append("Account no longer Dark!")
            resp.json('success', "Account is no longer Dark!", target=self.owner)
        self.owner.console_msg(msg)

    def report_clear(self, resp):
        msg = "Your Account is no longer Dark!"
        resp.success.append("Account no longer Dark!")
        resp.json('success', "Account is no longer Dark!", target=self.owner)
        self.owner.console_msg(msg)


class Hidden(BoolSetting):
    key = 'hidden'
    description = 'Stores whether owner is Hidden.'
    default = 0

    def report_change(self, resp):
        if self.value:
            msg = "Your Account is now Hidden!"
            resp.success.append("Account turned Hidden!")
            resp.json('success', "Account is now Hidden!", target=self.owner)
        else:
            msg = "Your Account is no longer Hidden!"
            resp.success.append("Account no longer Hidden!")
            resp.json('success', "Account is no longer Hidden!", target=self.owner)
        self.owner.console_msg(msg)

    def report_clear(self, resp):
        msg = "Your Account is no longer Hidden!"
        resp.success.append("Account no longer Hidden!")
        resp.json('success', "Account is no longer Hidden!", target=self.owner)
        self.owner.console_msg(msg)


ACCOUNT_SYSTEM_SETTINGS = (BannedUntil, TimeZoneSetting, ExtraCharacterSlots, DisableToggle, Dark, Hidden)
