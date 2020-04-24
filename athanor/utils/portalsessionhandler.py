import uuid
from evennia.server.portal.portalsessionhandler import PortalSessionHandler


class AthanorPortalSessionHandler(PortalSessionHandler):

    def generate_sessid(self):
        """
        Simply generates a sessid that's guaranteed to be unique for this Portal run.

        Returns:
            sessid
        """
        new_uuid = uuid.uuid4()
        if new_uuid in self:
            return self.generate_sessid()
        return new_uuid
