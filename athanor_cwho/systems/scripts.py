from athanor.systems.base import AthanorSystem

class CWhoSystem(AthanorSystem):
    """
    Global System Script that's responsible for managing an efficient list of all online accounts and characters
    without querying the SessionHandler. This script also sends out updates about visibility and idle/conn times
    of clients to GMCP recipients as needed.

    It is designed to send data only as needed to clients. We'll see how well that works out won't we?
    """

    key = 'cwho'
    system_name = 'WHO'
    interval = 60


    def load(self):

        # This Dictionary is a map of Character -> Who Can See Them
        self.character_visible_to = dict()

        # This Dictionary is Map of Character -> Who can they see?
        self.character_can_see = dict()

        # Subscribe all characters and Accounts online at load! ... which should be none.
        # But just in case.

        for character in self.systems['core'].characters:
            self.register_character(character)


    def register_character(self, character):
        """
        Method for adding a Character to the Character Who list.
        :param account:
        :return:
        """
        return
        # Figure out what other accounts can see this account.
        visible_to = set([char for char in self.systems['core'].characters if char.ath['cwho'].can_see(character)])
        self.character_visible_to[character] = visible_to

        # Then vice versa.
        can_see = set([char for char in self.systems['core'].characters if character.ath['cwho'].can_see(char)])
        self.character_can_see[character] = can_see

        # Now we need to announce this account to all other Accounts that can see it...
        self.announce_character(character)

        # And inform this account about all the Accounts that it can see!
        self.report_character(character)

    def report_character(self, character):
        data = list()
        for char in self.character_can_see[character]:
            data.append(char.ath['cwho'].gmcp_who(character))
        send_data = {'athanor_cwho': (('character', 'cwho', 'update_characters'), {'data': data})}
        character.msg(**send_data)

    def announce_character(self, character):
        for char in self.character_visible_to[character]:
            if char == character:
                continue
            data = character.ath['cwho'].gmcp_who(char)
            send_data = {'athanor_cwho': (('account', 'cwho', 'update_characters'), {'data': (data,)})}
            char.msg(**send_data)

    def remove_character(self, character):
        """
        Method that runs when a character fully logs out.

        :param character:
        :return:
        """
        return
        data = character.ath['cwho'].gmcp_remove()
        send_data = {'athanor_cwho': (('account', 'cwho', 'remove_characters'), {'data': (data,)})}
        for char in self.character_visible_to[character]:
            char.msg(**send_data)
        del self.character_visible_to[character]
        del self.character_can_see[character]

    def hide_character(self, character):
        """
        Method for alerting connected GMCP clients when to remove a character who has gone hidden/dark.
        From their perspective this should be no different from said character going offline.
        :param character:
        :return:
        """
        was_visible_to = self.character_visible_to[character]
        now_visible_to = set([char for char in was_visible_to if char.ath['cwho'].can_see(character)])

        # set arithmetic! This is a 'set difference'
        remove_from = was_visible_to - now_visible_to

        data = character.ath['cwho'].gmcp_remove()
        send_data = {'athanor_cwho': (('character', 'cwho', 'remove_characters'), {'data': (data,)})}
        for char in remove_from:
            char.msg(**send_data)

    def reveal_character(self, character):
        """
        Method for alerting connected GMCP clients when someone has removed their invisibility and gone public.
        From their perspective this should be no different from said character logging on.
        :param character:
        :return:
        """
        was_visible_to = self.character_visible_to[character]
        now_visible_to = set([char for char in was_visible_to if char.ath['cwho'].can_see(character)])

        # set arithmetic! This is a 'set difference'
        add_to = now_visible_to - was_visible_to

        for char in add_to:
            data = character.ath['cwho'].gmcp_who(char)
            send_data = {'athanor_cwho': (('character', 'cwho', 'update_characters'), {'data': (data,)})}
            char.msg(**send_data)


    def update_characters(self):
        for char in self.systems['core'].characters:
            # In the unlikely scenario that a character is in the set with no sessions, we'll remove 'em here.
            if not char.sessions.count():
                self.remove_character(char)
                continue  # No reason to report to a character who isn't connected!
            data = [cha.ath['cwho'].gmcp_who(char) for cha in self.systems['core'].characters_can_see[char]]
            send_data = {'athanor_cwho': (('character', 'cwho', 'update_characters'), {'data': data})}
            char.msg(**send_data)