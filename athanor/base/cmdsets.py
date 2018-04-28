from evennia.commands.cmdset import CmdSet
import athanor

class AthCmdSet(CmdSet):
    command_classes = tuple()
    prefix_mode = None

    def at_cmdset_creation(self):
        super(AthCmdSet, self).at_cmdset_creation()

        # get prefix from the athanor settings, if applicable.
        self.prefix = athanor.COMMAND_PREFIXES.get(self.prefix_mode, '')

        # Add all commands, applying the prefix and creating a link back to this CmdSet.
        for cmd in self.command_classes:
            self.add(cmd(key='%s%s' % (self.prefix, cmd.key), original_cmdset=self))


class AccountCmdSet(AthCmdSet):
    priority = -9


class CharacterCmdSet(AthCmdSet):
    priority = 1


class UnloggedCmdSet(AthCmdSet):
    priority = -19