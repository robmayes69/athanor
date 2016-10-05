from __future__ import unicode_literals

from athanor.commands.command import AthCommand

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
        characters = sorted(self.character.who.visible_characters(self.character),
                            key=lambda char: char.key)
        message = list()
        message.append(self.player.render.header('Who'))
        who_table = self.player.render.make_table(['Name', 'Alias', 'Fac', 'Idle', 'Conn', 'G', 'Location'],
                                                  width=[20, 11, 4, 5, 5, 2, 31])
        for char in characters:
            who_table.add_row(char.mxp_name(), '', '', char.time.last_or_idle_time(self.character),
                              char.time.last_or_conn_time(self.character),'?', char.location.key)
        message.append(who_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)