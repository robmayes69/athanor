from __future__ import unicode_literals

from athanor.commands.command import AthCommand
from athanor.library import connected_characters, connected_players, header, make_table

class CmdWho(AthCommand):
    """
    Displays all online characters.

    Usage:
        +who
    """
    key = '+who'
    system_name = 'WHO'
    help_category = 'Community'

    def func(self):
        characters = sorted(connected_characters(viewer=self.caller), key=lambda char: char.key)
        message = list()
        message.append(header('Who'))
        who_table = make_table('Name', 'Alias', 'Fac', 'Idle', 'Conn', 'G', 'Location', width=[20, 11, 4, 5, 5, 2, 31])
        for char in characters:
            who_table.add_row(char.mxp_name(), '', '', char.last_or_idle_time(self.caller),
                              char.last_or_conn_time(self.caller),'?', char.location.key)
        message.append(who_table)
        message.append(header())
        self.msg_lines(message)

class CmdPWho(AthCommand):
    """
    Displays all connected Players.

    Usage:
        +pwho
    """
    key = '+pwho'
    system_name = 'WHO'
    locks = "cmd:perm(Wizards)"
    help_category = 'Community'

    def func(self):
        players = sorted(connected_players(viewer=self.caller), key=lambda play: play.key)
        message = list()
        message.append(header('Who - Players'))
        who_table = make_table('Name', 'Idle', 'Conn', 'Characters', width=[20, 5, 5, 48])
        for play in players:
            who_table.add_row(play.key, play.last_or_idle_time(self.caller),
                              play.last_or_conn_time(self.caller), ", ".join([char.mxp_name() for char in play.get_all_puppets()]))
        message.append(who_table)
        message.append(header())
        self.msg_lines(message)