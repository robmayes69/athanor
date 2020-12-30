from athanor.utils.cmdset import BaseAthCmdSet
from athanor.zones.commands import CmdZone


class PlaytimeCmdSet(BaseAthCmdSet):
    key = "PlaytimeCmdSet"
    family = "playtime"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdZone)
