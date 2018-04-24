from __future__ import unicode_literals

from athanor.commands.base import AthCommand
from athanor.handlers.base import AthanorRequest


class CmdWho(AthCommand):
    """
    Displays all online characters.

    Usage:
        +who
        +who/idle to sort by idle times.
    """
    key = '+who2'
    system_name = 'WHO'
    help_category = 'Community'
    style = 'who'
    player_switches = ['idle', ]

    def _main(self):
        req = AthanorRequest(self.session, 'get_who_character')
        self.session.ath['athanor_who'].accept_request(req)

    def switch_idle(self):
        req = AthanorRequest(self.session, 'get_who_character', parameters={'sort': 'idle'})
        self.session.ath['athanor_who'].accept_request(req)


class CharacterCmdOOC(AthCommand):
    """
    stop puppeting and go ooc

    Usage:
        @ooc

    Go out-of-character (OOC).

    This will leave your current character and put you in a incorporeal OOC state.
    """

    key = "@ooc"
    locks = "cmd:pperm(Player)"
    aliases = "@unpuppet"
    help_category = "General"


    def _main(self):
        request = AthanorRequest(session=self.session, 
                                 operation='puppet_character', parameters={'character_id': 0})
        self.session.ath['athanor_system'].accept_request(request)


class CmdLook(AthCommand):
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Observes your location or objects in your vicinity.
    """
    key = "look2"
    aliases = ["l", "ls"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("You have no location to look at!")
                return
        else:
            target = caller.search(self.args)
            if not target:
                return
        self.msg(caller.at_look(self.session, target))
