from athanor.cmdsets.base import CharacterCmdSet as oldSet
from athanor.commands.characters import CmdWho, CmdLook, CharacterCmdOOC, CmdHelp, CmdShelp


class CoreCharacterCmdSet(oldSet):
    command_classes = (CmdLook, CharacterCmdOOC, CmdHelp, CmdShelp)


class WhoCharacterCmdSet(oldSet):
    command_classes = (CmdWho,)
