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
        if (psess := session.get_play_session()):
            base.update({
                'playsession': psess,
                'account': psess.get_account(),
                'player_character': psess.get_player_character(),
                'avatar': psess.get_avatar()
            })
            return base
        base['account'] = session.get_account()
        return base


class ServerSessionCmdSetHandler(AthanorCmdSetHandler):
    pass
