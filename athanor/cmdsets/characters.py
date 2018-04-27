from athanor.cmdsets.base import CharacterCmdSet as oldSet
from athanor.commands.characters import CmdLook, CharacterCmdOOC, CmdHelp, CmdShelp


class CoreCharacterCmdSet(oldSet):
    command_classes = (CmdLook, CharacterCmdOOC, CmdHelp, CmdShelp)
