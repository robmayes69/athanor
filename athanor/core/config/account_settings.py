from athanor.core.config.settings_templates import TimeZoneSetting, FutureSetting, SignedIntegerSetting
from athanor.core.config.settings_templates import UnsignedIntegerSetting, BoolSetting, RawTimeSetting
from athanor.utils.time import utcnow

class BannedUntil(FutureSetting):
    key = 'banned_until'
    description = 'Stores Timestamp of when ban duration is up. Only valid if stored value > Now.'
    owner_report = True
    admin_report = True

    def report_to_owner(self, enactor):
        if self.loaded:
            msg = 'Your Account has been banned Until: ' % (self.owner.owner.system.local_time(self.value))
        else:
            msg = 'Your Account has been un-banned!'
        self.owner.sys_msg(msg, enactor)
    
    def report_to_admin(self, enactor):
        if self.loaded:
            msg = 'Account has been banned Until: ' % (self.owner.owner.system.local_time(self.value))
        else:
            msg = 'Account has been un-banned!'
        self.owner.channel_alert(msg, enactor)
    
    def post_set(self):
        if self.loaded and self.value > utcnow():
            self.owner.owner.disconnect_all_sessions()


class TotalPlayTime(SignedIntegerSetting):
    key = 'total_play_time'
    description = 'Stores integer representing total seconds of connect time.'
    owner_report = False
    admin_report = False


class ExtraCharacterSlots(UnsignedIntegerSetting):
    key = 'extra_character_slots'
    description = 'Stores number of extra character slots. This builds on settings.py. Can be negative. End result floors at 0.'
    default = 0
    owner_report = True
    admin_report = True

    def report_to_owner(self, enactor):
        self.owner.sys_msg("Your Extra Character Slots was changed to: %s" % self.value, enactor)

    def report_to_admin(self, enactor):
        self.owner.channel_alert("Your Extra Character Slots was changed to: %s" % self.value, enactor)


class DisableToggle(BoolSetting):
    key = 'disabled'
    description = 'Stores data about whether the account is disabled. This supersedes Banning.'
    default = 0
    owner_report = True
    admin_report = True

    def report_to_owner(self, enactor):
        if self.value:
            msg = "Your Account has been disabled!"
        else:
            msg = "Your Account has been enabled!"
        self.owner.sys_msg(msg, enactor)
        
    def report_to_admin(self, enactor):
        if self.value:
            msg = "Account has been disabled!"
        else:
            msg = "Account has been enabled!"
        self.owner.channel_alert(msg, enactor)
        
    def post_set(self):
        if self.value:
            self.owner.owner.disconnect_all_sessions()


class LastPlayed(RawTimeSetting):
    key = 'last_played'
    description = 'Stores datetime of last session.'
    owner_report = False
    admin_report = False
    

class Dark(BoolSetting):
    key = 'dark'
    description = 'Stores whether owner is Dark.'
    default = 0
    owner_report = True
    admin_report = True

    def report_to_owner(self, enactor):
        if self.value:
            msg = "Your Account is now Dark!"
        else:
            msg = "Your Account is no longer Dark!"
        self.owner.sys_msg(msg, enactor)

    def report_to_admin(self, enactor):
        if self.value:
            msg = "Account is now Dark!"
        else:
            msg = "Account is no longer Dark!"
        self.owner.channel_alert(msg, enactor)

class Hidden(BoolSetting):
    key = 'hidden'
    description = 'Stores whether owner is Hidden.'
    default = 0
    owner_report = True
    admin_report = True

    def report_to_owner(self, enactor):
        if self.value:
            msg = "Your Account is now Hidden!"
        else:
            msg = "Your Account is no longer Hidden!"
        self.owner.sys_msg(msg, enactor)

    def report_to_admin(self, enactor):
        if self.value:
            msg = "Account is now Hidden!"
        else:
            msg = "Account is no longer Hidden!"
        self.owner.channel_alert(msg, enactor)
        
ACCOUNT_SYSTEM_SETTINGS = (BannedUntil, TotalPlayTime, TimeZoneSetting, ExtraCharacterSlots, 
                           DisableToggle, LastPlayed, Dark, Hidden)
