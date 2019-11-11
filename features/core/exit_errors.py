from evennia import Command, CmdSet


class ExitErrorCmd(Command):
    locks = "cmd:all()"
    arg_regex = r"\s|$"
    auto_help = False

    def func(self):
        self.caller.msg(f"You cannot go {self.key}.")


class ExitErrorNorth(ExitErrorCmd):
    key = 'north'
    aliases = ['n']


class ExitErrorSouth(ExitErrorCmd):
    key = 'south'
    aliases = ['s']


class ExitErrorEast(ExitErrorCmd):
    key = 'east'
    aliases = ['e']


class ExitErrorWest(ExitErrorCmd):
    key = 'west'
    aliases = ['w']


class ExitErrorSouthEast(ExitErrorCmd):
    key = 'southeast'
    aliases = ['se']


class ExitErrorSouthWest(ExitErrorCmd):
    key = 'southwest'
    aliases = ['sw']


class ExitErrorNorthEast(ExitErrorCmd):
    key = 'northeast'
    aliases = ['ne']


class ExitErrorNorthWest(ExitErrorCmd):
    key = 'northwest'
    aliases = ['nw']


class ExitErrorUp(ExitErrorCmd):
    key = 'up'
    aliases = ['u']


class ExitErrorDown(ExitErrorCmd):
    key = 'down'
    aliases = ['d']


class ExitErrorIn(ExitErrorCmd):
    key = 'in'


class ExitErrorOut(ExitErrorCmd):
    key = 'out'


EXIT_ERRORS = [ExitErrorNorth, ExitErrorNorthEast, ExitErrorNorthWest, ExitErrorEast, ExitErrorWest, ExitErrorSouth,
               ExitErrorSouthEast, ExitErrorSouthWest, ExitErrorUp, ExitErrorDown, ExitErrorIn, ExitErrorOut]


class ExitErrorCmdSet(CmdSet):

    def at_cmdset_creation(self):
        for cmd in EXIT_ERRORS:
            self.add(cmd)