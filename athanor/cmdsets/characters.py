from athanor.cmdsets.base import CharacterCmdSet as oldSet
from athanor.commands.characters import CmdWho, CmdLook, CharacterCmdOOC

class AthCoreCharacterCmdSet(oldSet):

    def at_cmdset_creation(self):
        self.add(CharacterCmdOOC)



class WhoCharacterCmdSet(oldSet):


    def at_cmdset_creation(self):
        self.add(CmdWho)
        self.add(CmdLook)