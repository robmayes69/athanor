from athanor.base.commands import AthCommand
import athanor


class CmdWho(AthCommand):
    """
    Displays all online accounts.

    Usage:
        [PREFIX]awho
        [PREFIX]awho/idle to sort by idle times.
    """
    key = 'awho'
    system_name = 'AWHO'
    help_category = 'Community'
    style = 'who'
    player_switches = ['idle', ]
    locks = 'cmd:perm(Admin)'

    def _main(self):
        response = athanor.SYSTEMS['awho'].render_console(self.session)
        self.msg(response)

    def switch_idle(self):
        response = athanor.SYSTEMS['awho'].render_console(self.session, params={'sort': 'idle'})
        self.msg(response)