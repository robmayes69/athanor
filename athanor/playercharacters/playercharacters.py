from django.conf import settings
from evennia.utils.utils import lazy_property
from athanor.playercharacters.handlers import PlayerCharacterSessionHandler, PlayerCharacterCmdHandler
from athanor.playercharacters.handlers import PlayerCharacterCmdSetHandler
from athanor.entities.entities import DefaultEntity


class DefaultPlayerCharacter(DefaultEntity):
    create_components = ('name', 'identity', 'player')
    _cmd_sort = 25
    _cmdset_types = ['player']
    _default_cmdset = settings.CMDSET_PLAYER_CHARACTER

    def cmd(self):
        return PlayerCharacterCmdHandler(self)

    @lazy_property
    def cmd(self):
        return PlayerCharacterCmdHandler(self)

    @lazy_property
    def cmdset(self):
        return PlayerCharacterCmdSetHandler(self, True)

    @lazy_property
    def sessions(self):
        return PlayerCharacterSessionHandler(self)

    def __repr__(self):
        return f"<PlayerCharacter({self.dbref}): {self.key}>"

    def __str__(self):
        return self.key

    def render_character_menu_line(self, looker):
        return self.key
