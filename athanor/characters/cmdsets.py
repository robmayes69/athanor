from athanor.base.cmdsets import CharacterCmdSet
from athanor.characters.commands import CmdLook, CharacterCmdOOC, CmdHelp, CmdShelp


class CoreCharacterCmdSet(CharacterCmdSet):
    command_classes = (CmdLook, CharacterCmdOOC, CmdHelp, CmdShelp)
