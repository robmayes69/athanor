from evennia.commands.cmdset import CmdSet


class AthanorCmdSet(CmdSet):
    """
    Slightly altered CmdSet that all Plugins should use and follow this approach for.
    """
    to_remove = []
    to_add = []

    @classmethod
    def remove_commands(cls, other_cmdset):
        for cmd in cls.to_remove:
            other_cmdset.remove(cmd)

    @classmethod
    def add_commands(cls, other_cmdset):
        for cmd in cls.to_add:
            other_cmdset.add(cmd)

    @classmethod
    def setup(cls, other_cmdset):
        cls.remove_commands(other_cmdset)

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        for cmd in self.to_add:
            self.add(cmd)
