from athanor.systems.base import SystemScript



class CoreSystem(SystemScript):
    """
    Global System Script that's responsible for updating play times. This has to run fairly regularly to insure against
    crashes and stupidity. However if the interval is too big, someone could randomly log in and get a big update.
    To K.I.S.S. I have set it at a humble interval of 1 minute.

    This depends on the Who System to maintain the characters and accounts .ndb interface.

    The Core is also responsible for keeping track of when people login and logout so other commands can reference
    the list of those currently online. Remember that this list is NOT visibility-filtered. Make sure to filter it if
    your game employs things like hiding from the who list.
    """

    key = 'core'
    system_name = 'SYSTEM'
    interval = 60

    def load(self):
        from athanor.utils.online import characters, accounts

        self.ndb.characters = set(characters())
        self.ndb.accounts = set(accounts())

    def at_repeat(self):
        for acc in self.ndb.accounts:
            acc.ath['core'].update_playtime(self.interval)

        for char in self.ndb.characters:
            char.ath['core'].update_playtime(self.interval)

    def register_account(self, account):
        """
        Method for adding an Account to the Account list.
        """
        # add them to the main set.
        self.ndb.accounts.add(account)

    def register_character(self, character):
        """
        Method for adding a Character to the Character list.
        """
        # add them to the main set.
        self.ndb.characters.add(character)

    def remove_account(self, account):
        """
        Method for removing an account from the active Account list.

        Args:
            account: an Account instance.

        Returns:
            None
        """
        self.ndb.accounts.remove(account)

    def remove_character(self, character):
        """
        Method for removing a character from the active Character list.

        Args:
            character:

        Returns:

        """
        self.ndb.characters.remove(character)


class WhoSystem(SystemScript):
    """
    Global System Script that's responsible for managing an efficient list of all online accounts and characters
    without querying the SessionHandler. This script also sends out updates about visibility and idle/conn times
    of clients to GMCP recipients as needed.

    It is designed to send data only as needed to clients. We'll see how well that works out won't we?
    """

    key = 'who'
    system_name = 'WHO'
    interval = 60


    def load(self):

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

        for character in self.systems['core'].ndb.characters:
            self.register_character(character)

        for account in self.systems['core'].ndb.accounts:
            self.register_account(account)

    def register_account(self, account):
        """
        Method for adding an Account to the Account Who list.
        :param account:
        :return:
        """

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
            data.append(acc.ath['who'].gmcp_who(acc))
        send_data = {'cmdname': (('account', 'who', 'update_accounts'), {'data': (data,)})}
        account.msg(**send_data)

    def announce_account(self, account):
        for acc in self.ndb.account_visible_to[account]:
            if acc == account:
                continue
            data = account.ath['who'].gmcp_who(acc)
            send_data = {'cmdname': (('account', 'who', 'update_accounts'), {'data': (data,)})}
            acc.msg(**send_data)

    def remove_account(self, account):
        """
        Method that runs when an account fully logs out.

        :param account:
        :return:
        """
        data = account.ath['who'].gmcp_remove()
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

        # Figure out what other accounts can see this account.
        visible_to = set([char for char in self.ndb.characters if char.ath['who'].can_see(character)])
        self.ndb.character_visible_to[character] = visible_to

        # Then vice versa.
        can_see = set([char for char in self.ndb.characters if character.ath['who'].can_see(char)])
        self.ndb.character_can_see[character] = can_see

        # Now we need to announce this account to all other Accounts that can see it...
        self.announce_character(character)

        # And inform this account about all the Accounts that it can see!
        self.report_character(character)



    def report_character(self, character):
        data = list()
        for char in self.ndb.character_can_see[character]:
            data.append(char.ath['who'].gmcp_who(character))
        send_data = {'cmdname': (('character', 'who', 'update_characters'), {'data': data})}
        character.msg(**send_data)

    def announce_character(self, character):
        for char in self.ndb.character_visible_to[character]:
            if char == character:
                continue
            data = character.ath['who'].gmcp_who(char)
            send_data = {'cmdname': (('account', 'who', 'update_characters'), {'data': (data,)})}
            char.msg(**send_data)

    def remove_character(self, character):
        """
        Method that runs when a character fully logs out.

        :param character:
        :return:
        """
        data = character.ath['who'].gmcp_remove()
        send_data = {'cmdname': (('account', 'who', 'remove_characters'), {'data': (data,)})}
        for char in self.ndb.character_visible_to[character]:
            char.msg(**send_data)
        del self.ndb.character_visible_to[character]
        del self.ndb.character_can_see[character]
        self.ndb.characters.remove(character)


    def hide_character(self, character):
        """
        Method for alerting connected GMCP clients when to remove a character who has gone hidden/dark.
        From their perspective this should be no different from said character going offline.
        :param character:
        :return:
        """
        was_visible_to = self.ndb.character_visible_to[character]
        now_visible_to = set([char for char in was_visible_to if char.ath['who'].can_see(character)])

        # set arithmetic! This is a 'set difference'
        remove_from = was_visible_to - now_visible_to

        data = character.ath['who'].gmcp_remove()
        send_data = {'cmdname': (('character', 'who', 'remove_characters'), {'data': (data,)})}
        for char in remove_from:
            char.msg(**send_data)

    def reveal_character(self, character):
        """
        Method for alerting connected GMCP clients when someone has removed their invisibility and gone public.
        From their perspective this should be no different from said character logging on.
        :param character:
        :return:
        """
        was_visible_to = self.ndb.character_visible_to[character]
        now_visible_to = set([char for char in was_visible_to if char.ath['who'].can_see(character)])

        # set arithmetic! This is a 'set difference'
        add_to = now_visible_to - was_visible_to

        for char in add_to:
            data = character.ath['who'].gmcp_who(char)
            send_data = {'cmdname': (('character', 'who', 'update_characters'), {'data': (data,)})}
            char.msg(**send_data)


    def hide_account(self, account):
        """
        Method for alerting connected GMCP clients when to remove an account who has gone hidden/dark.
        From their perspective this should be no different from said account going offline.
        :param account:
        :return:
        """
        was_visible_to = self.ndb.account_visible_to[account]
        now_visible_to = set([acc for acc in was_visible_to if acc.ath['who'].can_see(account)])

        # set arithmetic! This is a 'set difference'
        remove_from = was_visible_to - now_visible_to

        data = account.ath['who'].gmcp_remove()
        send_data = {'cmdname': (('account', 'who', 'remove_accounts'), {'data': (data,)})}
        for acc in remove_from:
            acc.msg(**send_data)


    def reveal_account(self, account):
        """
        Method for alerting connected GMCP clients when someone has removed their invisibility and gone public.
        From their perspective this should be no different from said account logging on.
        :param account:
        :return:
        """
        was_visible_to = self.ndb.character_visible_to[account]
        now_visible_to = set([char for char in was_visible_to if char.ath['who'].can_see(account)])

        # set arithmetic! This is a 'set difference'
        add_to = now_visible_to - was_visible_to

        for acc in add_to:
            data = account.ath['who'].gmcp_who(acc)
            send_data = {'cmdname': (('account', 'who', 'update_accounts'), {'data': (data,)})}
            acc.msg(**send_data)

    def at_repeat(self):
        """
        Every time the script runs we want to send out information like people's idle and connection times.
        :return:
        """
        pass
        #self.update_characters()
        #self.update_accounts()

    def update_characters(self):
        for char in self.ndb.characters:
            # In the unlikely scenario that a character is in the set with no sessions, we'll remove 'em here.
            if not char.sessions.count():
                self.remove_character(char)
                continue # No reason to report to a character who isn't connected!
            data = [cha.ath['who'].gmcp_who(char) for cha in self.ndb.character_can_see[char]]
            send_data = {'cmdname': (('character', 'who', 'update_characters'), {'data': data})}
            char.msg(**send_data)

    def update_accounts(self):
        for acc in self.ndb.accounts:
            # In the unlikely scenario that an account is in the set with no sessions, we'll remove 'em here.
            if not acc.sessions.count():
                self.remove_account(acc)
                continue # No reason to report to a character who isn't connected!
            data = [ac.ath['who'].gmcp_who(acc) for ac in self.ndb.account_can_see[acc]]
            send_data = {'cmdname': (('account', 'who', 'update_accounts'), {'data': data})}
            acc.msg(**send_data)
