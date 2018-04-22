from athanor.cmdsets.base import CharacterCmdSet as oldSet
from athanor.commands.characters import CmdWho, CmdLook

class AthCoreCharacterCmdSet(oldSet):
    pass



class WhoCharacterCmdSet(oldSet):


    def at_cmdset_creation(self):
        self.add(CmdWho)
        self.add(CmdLook)