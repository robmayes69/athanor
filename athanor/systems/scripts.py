from athanor.systems.base import AthanorSystem

from athanor.models import AccountOnline, CharacterOnline

class CoreSystem(AthanorSystem):
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
    load_order = -1000

    def reload(self):
        self.load()

    def load(self):
        characters = set([char.character for char in CharacterOnline.objects.all()])
        accounts = set([acc.account for acc in AccountOnline.objects.all()])
        self.characters = set(characters)
        self.accounts = set(accounts)

    def at_repeat(self):
        for acc in self.accounts:
            acc.ath['core'].update_playtime(self.interval)

        for char in self.characters:
            char.ath['core'].update_playtime(self.interval)

    def register_account(self, account):
        """
        Method for adding an Account to the Account list.
        """
        # add them to the main set.
        self.accounts.add(account)
        AccountOnline.objects.get_or_create(account=account)

    def register_character(self, character):
        """
        Method for adding a Character to the Character list.
        """
        # add them to the main set.
        self.characters.add(character)
        CharacterOnline.objects.get_or_create(character=character)

    def remove_account(self, account):
        """
        Method for removing an account from the active Account list.

        Args:
            account: an Account instance.

        Returns:
            None
        """
        self.accounts.remove(account)
        AccountOnline.objects.filter(account=account).delete()

    def remove_character(self, character):
        """
        Method for removing a character from the active Character list.

        Args:
            character:

        Returns:

        """
        self.characters.remove(character)
        CharacterOnline.objects.filter(character=character).delete()