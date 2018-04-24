from django.conf import settings
from evennia.utils import search
from athanor.commands.base import AthCommand
from athanor.handlers.base import AthanorRequest


class AccountCmdLook(AthCommand):
    key = 'look'
    aliases = ('dir', 'ls', 'l', 'view',)

    def _main(self):
        self.msg(self.account.at_look(target=self.account, session=self.session))


class AccountCmdIC(AthCommand):
    """
    control an object you have permission to puppet

    Usage:
      @ic <character>

    Go in-character (IC) as a given Character.

    This will attempt to "become" a different object assuming you have
    the right to do so. Note that it's the ACCOUNT character that puppets
    characters/objects and which needs to have the correct permission!

    You cannot become an object that is already controlled by another
    account. In principle <character> can be any in-game object as long
    as you the account have access right to puppet it.


    """

    key = "@ic"
    locks = "cmd:all()"
    aliases = "@puppet"
    help_category = "General"

    def _main(self):
        if not self.lhs_san:
            raise ValueError("Nothing entered to puppet!")
        character = self.partial(self.lhs_san, self.account.ath['athanor_characters'].all())
        if not character:
            raise ValueError("Character not found!")

        request = AthanorRequest(session=self.session,
                                 operation='puppet_character', parameters={'character_id': character.id})
        self.session.ath['athanor_system'].accept_request(request)


class AccountCmdCharCreate(AthCommand):

    key = '@charcreate'
    locks = 'cmd:pperm(Player)'
    help_category = 'General'

    def _main(self):
        request = AthanorRequest(session=self.session,
                                 operation='create_character', parameters={'name': self.lhs})
        self.session.ath['athanor_system'].accept_request(request)