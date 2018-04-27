from athanor.cmdsets.base import CharacterCmdSet

from athanor_cwho.commands.characters import CmdWho

class WhoCharacterCmdSet(CharacterCmdSet):
    command_classes = (CmdWho,)
