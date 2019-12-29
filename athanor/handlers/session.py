from django.conf import settings

_MULTISESSION_MODE = settings.MULTISESSION_MODE
_SESSIONS = None
_SESSID_MAX = 16 if _MULTISESSION_MODE in (1, 3) else 1


class ActorSessionHandler(object):

    def __init__(self, actor):
        self.actor = actor
        self.sessions = set()
        self.session_cache = dict()

    def get(self, sessid=None):
        if not sessid:
            return self.sessions
        return self.session_cache.get(sessid, None)

    def all(self):
        return self.sessions

    def add(self, session):
        self.sessions.add(session)
        self.session_cache[session.sessid] = session

    def remove(self, session):
        self.sessions.remove(session)
        del self.session_cache[session.sessid]

    def clear(self):
        self.sessions = set()
        self.session_cache = dict()


class CharacterSessionHandler(object):
    """
    Handles the get/setting of the sessid
    comma-separated integer field
    """

    def __init__(self, actor):
        """
        Initializes the handler.
        Args:
            obj (Object): The object on which the handler is defined.
        """
        self.actor = actor
        self.obj = actor.model
        self._sessid_cache = []
        self._recache()

    def _recache(self):
        global _SESSIONS
        if not _SESSIONS:
            from evennia.server.sessionhandler import SESSIONS as _SESSIONS
        self._sessid_cache = list(
            set(int(val) for val in (self.obj.db_sessid or "").split(",") if val)
        )
        if any(sessid for sessid in self._sessid_cache if sessid not in _SESSIONS):
            # cache is out of sync with sessionhandler! Only retain the ones in the handler.
            self._sessid_cache = [
                sessid for sessid in self._sessid_cache if sessid in _SESSIONS
            ]
            self.obj.db_sessid = ",".join(str(val) for val in self._sessid_cache)
            self.obj.save(update_fields=["db_sessid"])

    def get(self, sessid=None):
        """
        Get the sessions linked to this Object.
        Args:
            sessid (int, optional): A specific session id.
        Returns:
            sessions (list): The sessions connected to this object. If `sessid` is given,
                this is a list of one (or zero) elements.
        Notes:
            Aliased to `self.all()`.
        """
        global _SESSIONS
        if not _SESSIONS:
            from evennia.server.sessionhandler import SESSIONS as _SESSIONS
        if sessid:
            sessions = (
                [_SESSIONS[sessid] if sessid in _SESSIONS else None]
                if sessid in self._sessid_cache
                else []
            )
        else:
            sessions = [
                _SESSIONS[ssid] if ssid in _SESSIONS else None
                for ssid in self._sessid_cache
            ]
        if None in sessions:
            # this happens only if our cache has gone out of sync with the SessionHandler.
            self._recache()
            return self.get(sessid=sessid)
        return sessions

    def all(self):
        """
        Alias to get(), returning all sessions.
        Returns:
            sessions (list): All sessions.
        """
        return self.get()

    def add(self, session):
        """
        Add session to handler.
        Args:
            session (Session or int): Session or session id to add.
        Notes:
            We will only add a session/sessid if this actually also exists
            in the the core sessionhandler.
        """
        global _SESSIONS
        if not _SESSIONS:
            from evennia.server.sessionhandler import SESSIONS as _SESSIONS
        try:
            sessid = session.sessid
        except AttributeError:
            sessid = session

        sessid_cache = self._sessid_cache
        if sessid in _SESSIONS and sessid not in sessid_cache:
            if len(sessid_cache) >= _SESSID_MAX:
                return
            sessid_cache.append(sessid)
            self.obj.db_sessid = ",".join(str(val) for val in sessid_cache)
            self.obj.save(update_fields=["db_sessid"])

    def remove(self, session):
        """
        Remove session from handler.
        Args:
            session (Session or int): Session or session id to remove.
        """
        try:
            sessid = session.sessid
        except AttributeError:
            sessid = session

        sessid_cache = self._sessid_cache
        if sessid in sessid_cache:
            sessid_cache.remove(sessid)
            self.obj.db_sessid = ",".join(str(val) for val in sessid_cache)
            self.obj.save(update_fields=["db_sessid"])

    def clear(self):
        """
        Clear all handled sessids.
        """
        self._sessid_cache = []
        self.obj.db_sessid = None
        self.obj.save(update_fields=["db_sessid"])

    def count(self):
        """
        Get amount of sessions connected.
        Returns:
            sesslen (int): Number of sessions handled.
        """
        return len(self._sessid_cache)