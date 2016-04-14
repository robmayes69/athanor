from __future__ import unicode_literals

from evennia.utils.ansi import ANSIString
from typeclasses.characters import Character
from commands.command import AthCommand
from commands.library import utcnow, header, subheader, separator, make_table, sanitize_string
from world.database.fclist.models import FCList

class CmdFCList(AthCommand):
    """
    Documentation coming soon!
    """
    key = "+fclist"
    aliases = ["+theme"]
    locks = "cmd:all()"
    help_category = "Communications"
    player_switches = ['info', 'powers', 'mail']
    admin_switches = ['create', 'rename', 'delete', 'assign', 'remove', 'describe', 'setinfo', 'clearinfo',
                      'setpowers', 'clearpowers', 'status', 'type']
    system_name = 'FCLIST'

    def func(self):
        rhs = self.rhs
        lhs = self.lhs
        switches = self.final_switches