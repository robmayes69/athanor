from django.conf import settings
from evennia.server.sessionhandler import ServerSessionHandler
from evennia.utils.utils import class_from_module, delay,


PCONN = chr(1)  # portal session connect
PDISCONN = chr(2)  # portal session disconnect
PSYNC = chr(3)  # portal session sync
SLOGIN = chr(4)  # server session login
SDISCONN = chr(5)  # server session disconnect
SDISCONNALL = chr(6)  # server session disconnect all
SSHUTD = chr(7)  # server shutdown
SSYNC = chr(8)  # server session sync
SCONN = chr(11)  # server portal connection (for bots)
PCONNSYNC = chr(12)  # portal post-syncing session
PDISCONNALL = chr(13)  # portal session discnnect all
SRELOAD = chr(14)  # server reloading (have portal start a new server)
SSTART = chr(15)  # server start (portal must already be running anyway)
PSHUTD = chr(16)  # portal (+server) shutdown
SSHUTD = chr(17)  # server shutdown
PSTATUS = chr(18)  # ping server or portal status
SRESET = chr(19)  # server shutdown in reset mode


class AthanorServerSessionHandler(ServerSessionHandler):
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

        # Register the session to SessionHandler.
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
            session (Session): The Session to authenticate.
            account (Account): The Account identified as associated with this Session.
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
                session, operation=SLOGIN, sessiondata={"logged_in": True, "uid": session.uid}
            )

    def disconnect(self, session, reason="", sync_portal=True):
        """
        Called from server side to remove session and inform portal
        of this fact.

        Args:
            session (Session): The Session to disconnect.
            reason (str, optional): A motivation for the disconnect.
            sync_portal (bool, optional): Sync the disconnect to
                Portal side. This should be done unless this was
                called by self.portal_disconnect().

        """
        session = self.get(session.sessid)
        if not session:
            return
        sessid = session.sessid

        # Tell Session to stop everything, unlink all entities, and
        # say goodbye.
        session.at_disconnect(reason=reason)

        if sessid in self and not hasattr(self, "_disconnect_all"):
            del self[sessid]
        if sync_portal:
            # inform portal that session should be closed.
            self.server.amp_protocol.send_AdminServer2Portal(
                session, operation=SDISCONN, reason=reason
            )
