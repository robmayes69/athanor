from athanor.config.base import ConfigManager, ConfigManagerScript


class WhoManager(ConfigManagerScript):
    key = 'Who Manager'

    def at_script_creation(self):
        self.ndb.characters = set()
        self.ndb.accounts = set()
        self.desc = 'Maintains the Who List.'
        self.interval = 60
        self.repeats = 0

    def at_repeat(self):
        for char in self.ndb.characters:
            char.ath['system'].update_playtime(self.interval)
        for acc in self.ndb.accounts:
            acc.ath['system'].update_playtime(self.interval)

    def at_start(self):
        from athanor.utils.online import characters as _char, accounts as _account
        self.ndb.characters = _char()
        self.ndb.accounts = _account()

    def add_character(self, character):
        if character in self.ndb.characters:
            return
        self.ndb.characters.append(character)

    def rem_character(self, character):
        if character not in self.ndb.characters:
            return
        self.ndb.characters.remove(character)

    def add_account(self, account):
        if account in self.ndb.accounts:
            return
        self.ndb.characters.append(account)

    def rem_account(self, account):
        if account not in self.ndb.characters:
            return
        self.ndb.accounts.remove(account)

    def visible_characters(self, viewer):
        return [chr for chr in self.ndb.characters if viewer.ath['system'].can_see(chr)]

    def visible_accounts(self, viewer):
        return [chr for chr in self.ndb.characters if viewer.ath['system'].can_see(chr)]


ALL = [WhoManager, ]
