from athanor.base.cmdsets import CharacterCmdSet
from athanor_page.characters.commands import CmdPage

class PageCmdSet(CharacterCmdSet):
    command_classes = (CmdPage,)