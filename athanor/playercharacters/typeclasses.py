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

    def cmd(self):
        return PlayerCharacterCmdHandler(self)

    def at_identity_creation(self, validated, kwargs):
        # Should probably do something here about creating ObjectDB's... player avatars. By default.
        pass

    @lazy_property
    def cmd(self):
        raise PlayerCharacterCmdHandler(self)

    @lazy_property
    def cmdset(self):
        return PlayerCharacterCmdSetHandler(self, True)

    @lazy_property
    def sessions(self):
        return PlayerCharacterSessionHandler(self)

    @classmethod
    def create(cls, account, name, **kwargs):
        kwargs['account'] = account
        kwargs['autostart'] = False
        kwargs['interval'] = 10
        return cls.create_identity(name, **kwargs)
