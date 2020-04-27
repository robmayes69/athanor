from django.conf import settings
from evennia.server.sessionhandler import ServerSessionHandler
from evennia.utils.utils import class_from_module, delay
from evennia.server.portal import amp

from django.utils.translation import gettext as _


class AthanorServerSessionHandler(ServerSessionHandler):
    _server_session_class = class_from_module(settings.BASE_SERVER_SESSION_TYPECLASS)

    # AMP communication methods

    def get_or_create_session(self, sessiondata):
        address = sessiondata.pop('address')
        protocol = sessiondata.pop('protocol_key')
        django_key = sessiondata.pop('csessid', None)
        sessid = sessiondata.pop('sessid')
        print(f"RECEIVED SESSION DATA: {sessiondata}")
        sess = self._server_session_class.create(sessid, django_key, address, protocol, self)
        print(f"CREATED SESSION {sess}")
        sess.load_sync_data(sessiondata)
        print(f"SESS DICT {sess.__dict__}")

        # Register the session to ConnectionHandler.
        self[sessid] = sess

        # Ready the session for use, setting up its previous state as
        # appropriate.
        sess.at_sync()
        return sess

    def portal_connect(self, portalsessiondata):
        """
        Called by Portal when a new session has connected.
        Creates a new, unlogged-in game session.

        Args:
            portalsessiondata (dict): a dictionary of all property:value
                keys defining the session and which is marked to be
                synced.

        """
        sess = self.get_or_create_session(portalsessiondata)

        # show the first login command, may delay slightly to allow
        # the handshakes to finish.
        delay(settings.DELAY_COMMAND_LOGINSTART, self._run_cmd_login, sess)

    def portal_sessions_sync(self, portalsessionsdata):
        """
        Syncing all session ids of the portal with the ones of the
        server. This is instantiated by the portal when reconnecting.

        Args:
            portalsessionsdata (dict): A dictionary
              `{sessid: {property:value},...}` defining each session and
              the properties in it which should be synced.

        """
        old_sessions = set(self._server_session_class.objects.all())

        for sessid, sessdict in portalsessionsdata.items():
            sessdict['sessid'] = sessid
            sess = self.get_or_create_session(sessdict)
            if sess in old_sessions:
                old_sessions.remove(sess)

        self._server_session_class.objects.filter(id__in=old_sessions).update(db_is_active=False)

        mode = "reload"

        # tell the server hook we synced
        self.server.at_post_portal_sync(mode)
        # announce the reconnection
        self.announce_all(_(" ... Server restarted."))

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
