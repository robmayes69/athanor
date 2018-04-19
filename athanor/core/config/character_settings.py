
from athanor.core.config.account_settings import BannedUntil as oldBan, TotalPlayTime, DisableToggle as oldDis
from athanor.core.config.account_settings import LastPlayed, Dark as oldDark, Hidden as oldHidden, utcnow

class BannedUntil(oldBan):

    def report_to_owner(self, enactor):
        if self.loaded:
            msg = 'Your Character has been banned Until: ' % (self.owner.owner.system.local_time(self.value))
        else:
            msg = 'Your Character has been un-banned!'
        self.owner.sys_msg(msg, enactor)

    def report_to_admin(self, enactor):
        if self.loaded:
            msg = 'Character has been banned Until: ' % (self.owner.owner.system.local_time(self.value))
        else:
            msg = 'Character has been un-banned!'
        self.owner.channel_alert(msg, enactor)

    def post_set(self):
        if self.loaded and self.value > utcnow():
            pass # self.owner.owner.disconnect_all_sessions()

class DisableToggle(oldDis):

    def report_to_owner(self, enactor):
        if self.value:
            msg = "Your Character has been disabled!"
        else:
            msg = "Your Character has been enabled!"
        self.owner.sys_msg(msg, enactor)

    def report_to_admin(self, enactor):
        if self.value:
            msg = "Character has been disabled!"
        else:
            msg = "Character has been enabled!"
        self.owner.channel_alert(msg, enactor)

    def post_set(self):
        if self.value:
            pass # self.owner.owner.disconnect_all_sessions()


class Dark(oldDark):

    def report_to_owner(self, enactor):
        if self.value:
            msg = "Your Character is now Dark!"
        else:
            msg = "Your Character is no longer Dark!"
        self.owner.sys_msg(msg, enactor)

    def report_to_admin(self, enactor):
        if self.value:
            msg = "Character is now Dark!"
        else:
            msg = "Character is no longer Dark!"
        self.owner.channel_alert(msg, enactor)


class Hidden(oldHidden):

    def report_to_owner(self, enactor):
        if self.value:
            msg = "Your Character is now Hidden!"
        else:
            msg = "Your Character is no longer Hidden!"
        self.owner.sys_msg(msg, enactor)

    def report_to_admin(self, enactor):
        if self.value:
            msg = "Character is now Hidden!"
        else:
            msg = "Character is no longer Hidden!"
        self.owner.channel_alert(msg, enactor)


CHARACTER_SYSTEM_SETTINGS = (BannedUntil, TotalPlayTime, DisableToggle, LastPlayed, Dark, Hidden)

