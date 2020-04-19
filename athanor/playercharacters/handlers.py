from athanor.utils.link import EntitySessionHandler
from athanor.utils.cmdsethandler import AthanorCmdSetHandler
from athanor.utils.cmdhandler import CmdHandler


class PlayerCharacterSessionHandler(EntitySessionHandler):
    """
    Version of the SessionLink Handler that goes on PlayerCharacters (a subclass of Script).
    """

    def validate_link_request(self, session, force=False, sync=False, **kwargs):
        """
        This will always pass. No validation is needed, as that's handled at the PlaySession level.
        """
        pass

    def at_before_link_session(self, session, force=False, sync=False, **kwargs):
        """
        Nothing to do here either.
        """
        pass

    def at_link_session(self, session, force=False, sync=False, **kwargs):
        session.pcid = self.obj.pk
        session.pcharacter = self.obj

    def at_after_link_session(self, session, force=False, sync=False, **kwargs):
        pass

    def validate_unlink_request(self, session, force=False, reason=None, **kwargs):
        pass

    def at_before_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass

    def at_unlink_session(self, session, force=False, reason=None, **kwargs):
        session.pcid = None
        session.pcharacter = None

    def at_after_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass


class PlayerCharacterCmdSetHandler(AthanorCmdSetHandler):

    def get_channel_cmdsets(self, caller, merged_current):
        return []

    def gather_extra(self, caller, merged_current):
        cmdsets = []
        if not merged_current.no_channels:
            cmdsets.extend(self.get_channel_cmdsets(caller, merged_current))
        return cmdsets


class PlayerCharacterCmdHandler(CmdHandler):
    session = None

    def get_cmdobjects(self, session=None):
        cmdobjects = super().get_cmdobjects(session)
        cmdobjects['character'] = self.cmdobj
        if (session := cmdobjects.get('session', None)):
            cmdobjects['account'] = session.get_account()
            cmdobjects['puppet'] = session.get_puppet()
        return cmdobjects
