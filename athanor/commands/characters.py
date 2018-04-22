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
