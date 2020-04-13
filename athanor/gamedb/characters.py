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

    @property
    def cmdset_storage(self):
        return self.attributes.get(key="cmdset_storage", category="system", default=settings.CMDSET_CHARACTER)

    def cmd(self):
        return CharacterCmdHandler(self)

    @cmdset_storage.setter
    def cmdset_storage(self, value):
        self.attributes.add(key="cmdset_storage", category="system", value=value)

    def at_identity_creation(self, validated, kwargs):
        # Should probably do something here about creating ObjectDB's... player avatars. By default.
        pass

    @lazy_property
    def sessions(self):
        return CharacterSessionHandler(self)

    def at_cmdset_get(self, **kwargs):
        """
        Load Athanor CmdSets from settings.CMDSETs. Since an object miiiiight be more than one thing....
        """
        if self.ndb._cmdsets_loaded:
            return
        for cmdset_type in self._cmdset_types:
            for cmdset in settings.CMDSETS.get(cmdset_type):
                if not self.cmdset.has(cmdset):
                    self.cmdset.add(cmdset)
        self.ndb._cmdsets_loaded = True
