from django.conf import settings
from evennia.server.connectionhandler import ServerConnectionHandler
from evennia.utils.utils import class_from_module, delay
from evennia.server.portal import amp


class AthanorServerSessionHandler(ServerConnectionHandler):
    _server_session_class = class_from_module(settings.SERVER_SESSION_CLASS)

    # AMP communication methods

    def portal_connect(self, portalsessiondata):
        """
        Called by Portal when a new session has connected.
        Creates a new, unlogged-in game session.

        Args:
            portalsessiondata (dict): a dictionary of all property:value
                keys defining the session and which is marked to be
                synced.

        """

        sess = self._server_session_class(self)
        sess.load_sync_data(portalsessiondata)

        # Register the session to ConnectionHandler.
        self[sess.sessid] = sess

        # Ready the session for use, setting up its previous state as
        # appropriate.
        sess.at_sync()

        # show the first login command, may delay slightly to allow
        # the handshakes to finish.
        delay(settings.DELAY_COMMAND_LOGINSTART, self._run_cmd_login, sess)

    def login(self, session, account, force=False, testmode=False):
        """
        Log in the previously unloggedin session and the account we by
        now should know is connected to it. After this point we assume
        the session to be logged in one way or another.

        Args:
            session (Connection): The Connection to authenticate.
            account (Account): The Account identified as associated with this Connection.
            force (bool): Login also if the session thinks it's already logged in
                (this can happen for auto-authenticating protocols)
            testmode (bool, optional): This is used by unittesting for
                faking login without any AMP being actually active.

        """
        if session.logged_in and not force:
            # don't log in a session that is already logged in.
            return
        session.link('account', account, sync=False, testmode=testmode)

        # Update AMP.
        if not testmode:
            session.sessionhandler.server.amp_protocol.send_AdminServer2Portal(
                session, operation=amp.SLOGIN, sessiondata={"logged_in": True, "uid": session.uid}
            )

    def disconnect(self, session, reason="", sync_portal=True):
        """
        Called from server side to remove session and inform portal
        of this fact.

        Args:
            session (Connection): The Connection to disconnect.
            reason (str, optional): A motivation for the disconnect.
            sync_portal (bool, optional): Sync the disconnect to
                Portal side. This should be done unless this was
                called by self.portal_disconnect().

        """
        session = self.get(session.sessid)
        if not session:
            return
        sessid = session.sessid

        # Tell Connection to stop everything, unlink all entities, and
        # say goodbye.
        session.at_disconnect(reason=reason)

        if sessid in self and not hasattr(self, "_disconnect_all"):
            del self[sessid]
        if sync_portal:
            # inform portal that session should be closed.
            self.server.amp_protocol.send_AdminServer2Portal(
                session, operation=amp.SDISCONN, reason=reason
            )
