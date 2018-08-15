from athanor.base.cmdsets import CharacterCmdSet
from athanor.characters.commands import CmdLook, CmdHelp, CmdShelp, CmdAccount, CmdCharacter, CmdConfig


class CoreCharacterCmdSet(CharacterCmdSet):
    command_classes = (CmdLook, CmdHelp, CmdShelp, CmdAccount, CmdCharacter, CmdConfig)
