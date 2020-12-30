from athanor.utils.cmdhandler import CmdHandler
from athanor.utils.cmdsethandler import AthanorCmdSetHandler


class ServerSessionCmdHandler(CmdHandler):

    def __init__(self, cmdobj):
        super().__init__(cmdobj)
        self.session = cmdobj

    def get_cmdobjects(self, session=None):

        if not session:
            session = self.cmdobj
        base = {
            'session': session
        }
        if session.account:
            base['account'] = session.account
        if session.puppet:
            base['playtime'] = session.puppet
            base['puppet'] = session.puppet.db_current_puppet
        return base


class ServerSessionCmdSetHandler(AthanorCmdSetHandler):
    pass