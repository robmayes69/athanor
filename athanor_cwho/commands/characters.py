from athanor.commands.base import AthCommand
from athanor.handlers.base import AthanorRequest

class CmdWho(AthCommand):
    """
    Displays all online characters.

    Usage:
        +who
        +who/idle to sort by idle times.
    """
    key = '+who'
    system_name = 'WHO'
    help_category = 'Community'
    style = 'who'
    player_switches = ['idle', ]

    def _main(self):
        req = AthanorRequest(session=self.session, handler='cwho', operation='get_who_character')
        self.character.ath['cwho'].accept_request(req)

    def switch_idle(self):
        req = AthanorRequest(session=self.session, handler='cwho', operation='get_who_character', parameters={'sort': 'idle'})
        self.character.ath['cwho'].accept_request(req)