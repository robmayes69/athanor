from athanor.base.commands import AthCommand
from athanor.base.handlers import AthanorRequest
from athanor import AthException
from athanor.funcs.input import athanor as req_athanor


class CmdLook(AthCommand):
    key = 'look'
    aliases = ('dir', 'ls', 'l', 'view','login')

    def _main(self):
        self.msg(self.account.at_look(target=self.account, session=self.session))


class CmdIC(AthCommand):
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
            raise AthException("Nothing entered to puppet!")
        character = self.partial(self.lhs_san, self.account.ath['character'].all())
        if not character:
            raise AthException("Character not found!")

        req_athanor(self.session, 'session', 'core', 'puppet_character', {'character_id': character})


class CmdCharCreate(AthCommand):

    key = '@charcreate'
    locks = 'cmd:pperm(Player)'
    help_category = 'General'

    def _main(self):
        req_athanor(self.session, 'account', 'core', 'create_character', {'name': self.lhs})


class CmdQuit(AthCommand):
    """
    quit the game

    Usage:
      @quit

    Switch:
      all - disconnect all connected sessions

    Gracefully disconnect your current session from the
    game. Use the /all switch to disconnect from all sessions.
    """
    key = "@quit"
    locks = "cmd:all()"

    def _main(self):
        req_athanor(self.session, 'account', 'core', 'disconnect', params={'all': False})

    def switch_all(self):
        req_athanor(source=self.session, manager='account', handler='core', operation='disconnect',
                    output=('text','gmcp'), params={'all': True})