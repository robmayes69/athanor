from athanor.base.cmdsets import CharacterCmdSet
from athanor_ooc.characters.commands import CmdOOC


class OOCCmdset(CharacterCmdSet):
    key = 'ooc'
    command_classes = (CmdOOC,)