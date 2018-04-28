from athanor.base.help import HelpFile


class WhoHelpFile(HelpFile):
    """
    # Commands
    __+who__ - Show all visible, connected players.
    __+who/idle__ - Like above, but sorts by idle times.
    __+who <text>__ - Search for online players starting with <text>.
    * Testing bullet.
    """
    key = "+who"
    category = 'Community'

