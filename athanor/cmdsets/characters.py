from athanor.cmdsets.base import CharacterCmdSet as oldSet
from athanor.commands.characters import CmdWho, CmdLook, CharacterCmdOOC

class CoreCharacterCmdSet(oldSet):

    def at_cmdset_creation(self):
        self.add(CharacterCmdOOC)
        self.add(CmdLook)


class WhoCharacterCmdSet(oldSet):


    def at_cmdset_creation(self):
        self.add(CmdWho)
