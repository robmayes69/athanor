from athanor.base.commands import AthCommand
import athanor


class CmdWho(AthCommand):
    """
    Displays all online characters.

    Usage:
        [PREFIX]who
        [PREFIX]who/idle to sort by idle times.
    """
    key = 'who'
    system_name = 'WHO'
    help_category = 'Community'
    style = 'who'
    player_switches = ['idle', ]

    def _main(self):
        response = athanor.SYSTEMS['cwho'].render_console(self.session)
        self.msg(response)

    def switch_idle(self):
        response = athanor.SYSTEMS['cwho'].render_console(self.session, params={'sort': 'idle'})
        self.msg(response)