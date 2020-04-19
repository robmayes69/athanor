from athanor.utils.cmdsethandler import AthanorCmdSetHandler
from athanor.utils.cmdhandler import CmdHandler


class PlaySessionCmdSetHandler(AthanorCmdSetHandler):
    pass


class PlaySessionCmdHandler(CmdHandler):

    def get_cmdobjects(self, session=None):
        cmdobjects = super().get_cmdobjects(session)
        cmdobjects['playsession'] = self.cmdobj
        # this should never be None.
        cmdobjects['account'] = self.cmdobj.get_account()
        # Nor should this.
        cmdobjects['player_character'] = self.cmdobj.get_player_character()
        # this might be none! And that is fine.
        cmdobjects['avatar'] = self.cmdobj.get_avatar()
        return cmdobjects
