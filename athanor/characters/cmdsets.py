from athanor.base.cmdsets import CharacterCmdSet
from athanor.characters.commands import CmdLook, CmdHelp, CmdShelp


class CoreCharacterCmdSet(CharacterCmdSet):
    command_classes = (CmdLook, CmdHelp, CmdShelp)
