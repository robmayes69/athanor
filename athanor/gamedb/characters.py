from athanor.gamedb.scripts import AthanorIdentityScript
from athanor.gamedb.base import HasCmdSets


class AthanorPlayerCharacter(AthanorIdentityScript, HasCmdSets):
    _namespace = "player_character"
    _verbose_name = 'Player Character'
    _verbose_name_plural = "Player Characters"

    def at_identity_creation(self, validated):
        # Should probably do something here about creating ObjectDB's... player avatars.
        pass

