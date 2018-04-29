from athanor.base.cmdsets import CharacterCmdSet

from athanor_cwho.characters.commands import CmdWho

class WhoCmdSet(CharacterCmdSet):
    key = 'cwho'
    command_classes = (CmdWho,)
