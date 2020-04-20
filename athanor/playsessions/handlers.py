from django.conf import settings
from athanor.utils.cmdsethandler import AthanorCmdSetHandler
from athanor.utils.cmdhandler import CmdHandler
from athanor.utils.link import EntitySessionHandler

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


class PlaySessionSessionHandler(EntitySessionHandler):

    def validate_link_request(self, session, force=False, sync=False, **kwargs):
        """
        Nothing really to do here. Yet.
        """
        pass

    def at_before_link_session(self, session, force=False, sync=False, **kwargs):
        pass

    def at_link_session(self, session, force=False, sync=False, **kwargs):
        session.swap_cmdset(settings.CMDSET_ACTIVE)

    def at_after_link_session(self, session, force=False, sync=False, **kwargs):
        if sync:
            return
        if not self.obj.is_active:
            self.obj.start()
        if not self.obj.db.character.is_active:
            self.obj.db.character.start()

    def validate_unlink_request(self, session, force=False, reason=None, **kwargs):
        pass

    def at_before_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass

    def at_unlink_session(self, session, force=False, reason=None, **kwargs):
        session.swap_cmdset(settings.SELECT_SCREEN)

    def at_after_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass
