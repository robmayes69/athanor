from __future__ import unicode_literals

from athanor.commands.base import AthCommand

class CmdWho(AthCommand):
    """
    Displays all online characters.

    Usage:
        +who
    """
    key = '+who'
    system_name = 'WHO'
    help_category = 'Community'
    style = 'who'

    def func(self):
        characters = sorted(self.character.managers['Who Manager'].visible_characters(self.character),
                            key=lambda char: char.key)
        message = list()
        message.append(self.character.styles.header('Who', style=self.style))
        who_table = self.character.styles.make_table(['Name', 'Alias', 'Fac', 'Idle', 'Conn', 'G', 'Location'],
                                                  width=[20, 11, 4, 5, 5, 2, 33], style=self.style)
        for char in characters:
            who_table.add_row(char.ath['system'].mxp_name(), '', '', char.ath['system'].last_or_idle_time(self.character),
                              char.ath['system'].last_or_conn_time(self.character),'?', char.location.key)
        message.append(who_table)
        message.append(self.character.styles.footer(self.style))
        self.msg_lines(message)