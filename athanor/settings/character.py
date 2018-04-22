from athanor.settings.account import BannedUntil as oldBan, DisableToggle as oldDis
from athanor.settings.account import Dark as oldDark, Hidden as oldHidden, utcnow


class BannedUntil(oldBan):

    def report_change(self, resp):
        if self.loaded:
            resp.success.append("Character Banned until: ${localtime,%s}") % self.value_storage
            resp.json('success', message='Character Banned', target=self.owner, timestamp=self.value_storage)
            msg = 'Your Character has been banned Until: ${localtime,%s}' % self.value_storage
        else:
            msg = 'Your Character has been un-banned!'
            resp.success.append("Character un-banned!")
            resp.json('success', message='Character un-banned!', target=self.owner)
        self.handler.console_msg(msg)

    def report_clear(self, resp):
        msg = 'Your Character has been un-banned!'
        resp.success.append("Character un-banned!")
        resp.json('success', message='Character un-banned!', target=self.owner)
        self.handler.console_msg(msg)

    def post_set(self):
        if self.loaded and self.value > utcnow():
            pass # self.owner.owner.disconnect_all_sessions()


class DisableToggle(oldDis):

    def report_change(self, resp):
        if self.value:
            msg = "Your Character has been disabled!"
            resp.success.append("Character Disabled!")
            resp.json('success', message='Character Disabled', target=self.owner)
        else:
            msg = "Your Character has been enabled!"
            resp.success.append("Character Enabled!")
            resp.json('success', message='Character Enabled!', target=self.owner)
        self.handler.console_msg(msg)

    def report_clear(self, resp):
        msg = "Your Character has been enabled!"
        resp.success.append("Character Enabled!")
        resp.json('success', message='Character Enabled!', target=self.owner)
        self.handler.console_msg(msg)

    def post_set(self):
        if self.value:
            pass # self.owner.owner.disconnect_all_sessions()


class Dark(oldDark):

    def report_change(self, resp):
        if self.value:
            msg = "Your Character is now Dark!"
            resp.success.append("Character turned Dark!")
            resp.json('success', "Character is now Dark!", target=self.owner)
        else:
            msg = "Your Character is no longer Dark!"
            resp.success.append("Character no longer Dark!")
            resp.json('success', "Character is no longer Dark!", target=self.owner)
        self.owner.console_msg(msg)

    def report_clear(self, resp):
        msg = "Your Character is no longer Dark!"
        resp.success.append("Character no longer Dark!")
        resp.json('success', "Character is no longer Dark!", target=self.owner)
        self.owner.console_msg(msg)


class Hidden(oldHidden):

    def report_change(self, resp):
        if self.value:
            msg = "Your Character is now Hidden!"
            resp.success.append("Character turned Hidden!")
            resp.json('success', "Character is now Hidden!", target=self.owner)
        else:
            msg = "Your Character is no longer Hidden!"
            resp.success.append("Character no longer Hidden!")
            resp.json('success', "Character is no longer Hidden!", target=self.owner)
        self.owner.console_msg(msg)

    def report_clear(self, resp):
        msg = "Your Character is no longer Hidden!"
        resp.success.append("Character no longer Hidden!")
        resp.json('success', "Character is no longer Hidden!", target=self.owner)
        self.owner.console_msg(msg)


CHARACTER_SYSTEM_SETTINGS = (BannedUntil, DisableToggle, Dark, Hidden)

