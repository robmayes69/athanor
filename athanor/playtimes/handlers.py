from athanor.utils.cmdsethandler import AthanorCmdSetHandler
from athanor.utils.cmdhandler import CmdHandler


class PlaytimeCmdSetHandler(AthanorCmdSetHandler):
    pass


class PlaytimeCmdHandler(CmdHandler):

    def get_cmdobjects(self, session=None):
        if session:
            return session.cmd.get_cmdobjects()
        return {
            'playtime': self.cmdobj,
            'puppet': self.cmdobj.db_current_puppet
        }
