from athanor.utils.cmdsethandler import AthanorCmdSetHandler
from athanor.utils.cmdhandler import CmdHandler
from athanor.access.acl import ACLHandler


class EntityCmdHandler(CmdHandler):

    def get_cmdobjects(self, session=None):
        if session:
            return session.cmd.get_cmdobjects()
        return {
            'puppet': self.cmdobj
        }


class EntityCmdSetHandler(AthanorCmdSetHandler):
    pass


class EntityAclHandler(ACLHandler):
    pass
