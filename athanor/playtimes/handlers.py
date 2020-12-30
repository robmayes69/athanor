from athanor.utils.cmdsethandler import AthanorCmdSetHandler
from athanor.utils.cmdhandler import CmdHandler


class PlaytimeCmdSetHandler(AthanorCmdSetHandler):

    def get_channel_cmdsets(self, caller, merged_current):
        if (identity := self.obj.get_identity()):
            return [identity.channels.cmdset()]
        return []

    def gather_extra(self, caller, merged_current):
        cmdsets = []
        if not merged_current.no_channels:
            cmdsets.extend(self.get_channel_cmdsets(caller, merged_current))
        return cmdsets


class PlaytimeCmdHandler(CmdHandler):

    def get_cmdobjects(self, session=None):
        if session:
            return session.cmd.get_cmdobjects()
        return {
            'playtime': self.cmdobj,
            'puppet': self.cmdobj.db_current_puppet
        }
