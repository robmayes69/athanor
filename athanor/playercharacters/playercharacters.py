from django.conf import settings
from evennia.utils.utils import lazy_property
from athanor.playercharacters.handlers import PlayerCharacterSessionHandler, PlayerCharacterCmdHandler
from athanor.playercharacters.handlers import PlayerCharacterCmdSetHandler
from athanor.identities.identities import DefaultIdentity


class DefaultPlayerCharacter(DefaultIdentity):
    _namespace = "playercharacters"
    _verbose_name = 'Player Character'
    _verbose_name_plural = "Player Characters"
    _cmd_sort = 25
    _cmdset_types = ['player']
    _default_cmdset = settings.CMDSET_PLAYER_CHARACTER

    def cmd(self):
        return PlayerCharacterCmdHandler(self)

    def at_identity_creation(self, validated, **kwargs):
        validated['account'].link_identity(self)
        self.at_setup_player(validated, **kwargs)

    def at_setup_player(self, validated, **kwargs):
        """
        This would be a good spot to create avatar Entities...
        """
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
    def _validate_identity(cls, name, clean_name, namespace, kwargs):
        results = dict()
        if not (account := kwargs.pop('account', None)):
            raise ValueError("Player characters must be assigned to an Account!")
        results['account'] = account
        return results, kwargs


    def __repr__(self):
        return f"<PlayerCharacter({self.dbref}): {self.key}>"

    def __str__(self):
        return self.key

    def render_character_menu_line(self, looker):
        return self.key
