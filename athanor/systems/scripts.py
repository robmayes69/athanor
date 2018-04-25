from athanor.systems.base import SystemScript

class WhoSystem(SystemScript):

    key = 'who'
    system_name = 'WHO'


    def load(self):
        from athanor.utils.online import characters, accounts

        self.ndb.characters = set()
        self.ndb.accounts = set()

        # This Dictionary is a map of Character -> Who Can See Them
        self.ndb.character_visible_to = dict()

        # This Dictionary is Map of Character -> Who can they see?
        self.ndb.character_can_see = dict()

        # This Dictionary is a Map of Account -> Who Can See Them?
        self.ndb.account_visible_to = dict()

        # This Dictionary is a Map of Account -> Who can they see?
        self.ndb.account_can_see = dict()

        # Subscribe all characters and Accounts online at load! ... which should be none.
        # But just in case.

        for character in characters():
            self.register_character(character)

        for account in accounts():
            self.register_account(account)

    def register_account(self, account):
        """
        Method for adding an Account to the Account Who list.
        :param account:
        :return:
        """
        # First add them to the main set.
        self.ndb.accounts.add(account)

        # Figure out what other accounts can see this account.
        visible_to = set([acc for acc in self.ndb.accounts if acc.ath['who'].can_see(account)])
        self.ndb.account_visible_to[account] = visible_to

        # Then vice versa.
        can_see = set([acc for acc in self.ndb.accounts if account.ath['who'].can_see(acc)])
        self.ndb.account_can_see[account] = can_see

        # Now we need to announce this account to all other Accounts that can see it...
        self.announce_account(account)

        # And inform this account about all the Accounts that it can see!
        self.report_account(account)


    def report_account(self, account):
        data = list()
        for acc in self.ndb.account_can_see[account]:
            data.append(acc.ath['who'].gmcp_who())
        send_data = {'cmdname': (('account', 'who', 'update_accounts'), {'data': (data,)})}
        account.msg(**send_data)

    def announce_account(self, account):
        data = account.ath['who'].gmcp_who()
        send_data = {'cmdname': (('account', 'who', 'update_accounts'), {'data': (data,)})}
        for acc in self.ndb.account_visible_to[account]:
            acc.msg(**send_data)

    def remove_account(self, account):
        """
        Method that runs when an account fully logs out.

        :param account:
        :return:
        """
        data = account.ath['who'].gmcp_who()
        send_data = {'cmdname': (('account', 'who', 'remove_accounts'), {'data': (data,)})}
        for acc in self.ndb.account_visible_to[account]:
            acc.msg(**send_data)
        del self.ndb.account_visible_to[account]
        del self.ndb.account_can_see[account]
        self.ndb.accounts.remove(account)

    def register_character(self, character):
        """
        Method for adding a Character to the Character Who list.
        :param account:
        :return:
        """
        # First add them to the main set.
        self.ndb.characters.add(character)

        # Figure out what other accounts can see this account.
        visible_to = set([char for char in self.ndb.accounts if char.ath['who'].can_see(character)])
        self.ndb.character_visible_to[character] = visible_to

        # Then vice versa.
        can_see = set([char for char in self.ndb.accounts if character.ath['who'].can_see(char)])
        self.ndb.character_can_see[character] = can_see

        # Now we need to announce this account to all other Accounts that can see it...
        self.announce_character(character)

        # And inform this account about all the Accounts that it can see!
        self.report_character(character)

    def report_character(self, character):
        data = list()
        for char in self.ndb.account_can_see[character]:
            data.append(char.ath['who'].gmcp_who())
        send_data = {'cmdname': (('character', 'who', 'update_characters'), {'data': (data,)})}
        character.msg(**send_data)

    def announce_character(self, character):
        data = character.ath['who'].gmcp_who()
        send_data = {'cmdname': (('account', 'who', 'update_characters'), {'data': (data,)})}
        for char in self.ndb.account_visible_to[character]:
            char.msg(**send_data)

    def remove_character(self, character):
        """
        Method that runs when a character fully logs out.

        :param character:
        :return:
        """
        data = character.ath['who'].gmcp_who()
        send_data = {'cmdname': (('account', 'who', 'remove_characters'), {'data': (data,)})}
        for char in self.ndb.character_visible_to[character]:
            char.msg(**send_data)
        del self.ndb.character_visible_to[character]
        del self.ndb.character_can_see[character]
        self.ndb.characters.remove(character)


    def hide_character(self, character):
        pass


    def reveal_character(self, character):
        pass


    def hide_account(self, account):
        pass


    def reveal_account(self, account):
        pass

    def at_repeat(self):
        """
        Every time the script runs we want to send out information like people's idle and connection times.
        :return:
        """
        self.update_characters()
        self.update_accounts()

    def update_characters(self):
        characters_dict = {char: char.ath['who'].gmcp_who() for char in self.ndb.characters}
        for char in self.ndb.characters:
            # In the unlikely scenario that a character is in the set with no sessions, we'll remove 'em here.
            if not char.sessions.count():
                self.remove_character(char)
                continue # No reason to report to a character who isn't connected!
            data = [characters_dict[cha] for cha in self.ndb.character_can_see[char]]
            send_data = {'cmdname': (('account', 'who', 'update_characters'), {'data': (data,)})}
            char.msg(**send_data)

    def update_accounts(self):
        accounts_dict = {acc: acc.ath['who'].gmcp_who() for acc in self.ndb.accounts}
        for acc in self.ndb.accounts:
            # In the unlikely scenario that an account is in the set with no sessions, we'll remove 'em here.
            if not acc.sessions.count():
                self.remove_account(acc)
                continue # No reason to report to a character who isn't connected!
            data = [accounts_dict[ac] for acc in self.ndb.character_can_see[acc]]
            send_data = {'cmdname': (('account', 'who', 'update_accounts'), {'data': (data,)})}
            acc.msg(**send_data)
