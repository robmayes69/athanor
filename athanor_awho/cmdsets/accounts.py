from athanor.cmdsets.base import CharacterCmdSet

from athanor_who.commands.character import CmdWho

class WhoCharacterCmdSet(CharacterCmdSet):

    def at_cmdset_creation(self):
        self.add(CmdWho)