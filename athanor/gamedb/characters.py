from django.conf import settings
from evennia.utils.utils import lazy_property
from athanor.gamedb.scripts import AthanorIdentityScript
from athanor.utils.mixins import HasCommands
from athanor.utils.link import CharacterSessionHandler
from athanor.commands.cmdhandler import CharacterCmdHandler


class AthanorPlayerCharacter(AthanorIdentityScript, HasCommands):
    _namespace = "player_character"
    _verbose_name = 'Player Character'
    _verbose_name_plural = "Player Characters"
    _cmd_sort = 25
    _cmdset_types = ['character']

    def cmd(self):
        return CharacterCmdHandler(self)

    def at_identity_creation(self, validated, kwargs):
        # Should probably do something here about creating ObjectDB's... player avatars. By default.
        pass

    @lazy_property
    def sessions(self):
        return CharacterSessionHandler(self)
