from evennia.commands.cmdsethandler import CmdSetHandler


class AthanorCmdSetHandler(CmdSetHandler):

    def gather(self, caller, merged_current):
        """
        Called by CmdHandler when merging cmdsets. This must return the local cmdset_stack
        as well as gather any 'extra cmdsets' such as from local objects or channels.

        Args:
            caller (obj): The executor of the command. usually a ObjectDB, AccountDB, SEssion, etc.
            merged_current: The merged current cmdset in its present state. used for filtering
                rules.

        Returns:
            cmdset stack (list): A list of Cmdsets that have been gathered.
        """
        stack = list(self.cmdset_stack)
        stack.extend(self.gather_extra(caller, merged_current))

    def gather_extra(self, caller, merged_current):
        return []


class AccountCmdSetHandler(AthanorCmdSetHandler):

    def get_channel_cmdsets(self, caller, merged_current):
        return []

    def gather_extra(self, caller, merged_current):
        cmdsets = []
        if not merged_current.no_channels:
            cmdsets.extend(self.get_channel_cmdsets(caller, merged_current))
        return cmdsets


class PlayerCharacterCmdSetHandler(AthanorCmdSetHandler):

    def get_channel_cmdsets(self, caller, merged_current):
        return []

    def gather_extra(self, caller, merged_current):
        cmdsets = []
        if not merged_current.no_channels:
            cmdsets.extend(self.get_channel_cmdsets(caller, merged_current))
        return cmdsets


class PuppetCmdSetHandler(AthanorCmdSetHandler):

    def get_neighbors(self):
        location = self.obj.location
        neighbors = list(self.obj.contents_get())
        if location:
            neighbors.append(location)
            neighbors.extend(location.contents_get(exclude=self.obj))
        return [obj for obj in neighbors if not obj._is_deleted]

    def get_callable_neighbors(self, caller):
        return [obj for obj in self.get_neighbors() if hasattr(obj, 'cmdset') and
                obj.access(caller, 'call', no_superuser_bypass=True)]

    def get_neighbor_cmdsets(self, caller, merged_current):
        cmdsets = []
        neighbors = self.get_callable_neighbors(caller)
        for obj in neighbors:
            yield obj.at_cmdset_get()
        for obj in neighbors:
            cmdsets.extend(obj.cmdset.get())
        if merged_current.no_exits:
            return [cset for cset in cmdsets if cset.key != "ExitCmdSet"]
        return cmdsets

    def gather_extra(self, caller, merged_current):
        cmdsets = []
        if not merged_current.no_objs:
            cmdsets.extend(self.get_neighbor_cmdsets(caller, merged_current))
        return cmdsets
