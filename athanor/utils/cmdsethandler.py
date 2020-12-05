from evennia.commands.cmdsethandler import CmdSetHandler


class AthanorCmdSetHandler(CmdSetHandler):

    def gather(self, caller, merged_current):
        """
        Called by CmdHandler when merging cmdsets. This must return the local cmdset_stack
        as well as gather any 'extra cmdsets' such as from local objdb or channels.

        Args:
            caller (obj): The executor of the command. usually a ObjectDB, AccountDB, SEssion, etc.
            merged_current: The merged current cmdset in its present state. used for filtering
                rules.

        Returns:
            cmdset stack (list): A list of Cmdsets that have been gathered.
        """
        stack = list(self.cmdset_stack)
        stack.extend(self.gather_extra(caller, merged_current))
        return stack

    def gather_extra(self, caller, merged_current):
        return []
