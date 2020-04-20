from django.conf import settings
from evennia.utils.utils import lazy_property
from athanor.identities.typeclasses import AthanorIdentityScript
from athanor.playercharacters.handlers import PlayerCharacterSessionHandler, PlayerCharacterCmdHandler
from athanor.playercharacters.handlers import PlayerCharacterCmdSetHandler


class AthanorPlayerCharacter(AthanorIdentityScript):
    _namespace = "playercharacters"
    _verbose_name = 'Player Character'
    _verbose_name_plural = "Player Characters"
    _cmd_sort = 25
    _cmdset_types = ['character']
    _default_cmdset = settings.CMDSET_PLAYER_CHARACTER

    def cmd(self):
        return PlayerCharacterCmdHandler(self)

    def at_identity_creation(self, validated, **kwargs):
        # Should probably do something here about creating ObjectDB's... player avatars. By default.
        pass

    @lazy_property
    def cmd(self):
        return PlayerCharacterCmdHandler(self)

    @lazy_property
    def cmdset(self):
        return PlayerCharacterCmdSetHandler(self, True)

    @lazy_property
    def sessions(self):
        return PlayerCharacterSessionHandler(self)

    @classmethod
    def create_playercharacter(cls, account, name, **kwargs):
        kwargs['account'] = account
        kwargs['autostart'] = False
        kwargs['interval'] = 10
        return cls.create_identity(name, **kwargs)

    def __repr__(self):
        return f"<PlayerCharacter({self.dbref}): {self.key}>"

    def __str__(self):
        return self.key

    def render_character_menu_line(self, looker):
        return self.key
