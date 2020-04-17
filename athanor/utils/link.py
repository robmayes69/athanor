import time
from datetime import timezone
from django.conf import settings

from evennia import MONITOR_HANDLER


class EntitySessionHandler:
    """
    Handles adding/removing session references to an Account, Puppet, or perhaps
    stranger things down the line.
    """

    def __init__(self, obj):
        """
        Initializes the handler.
        Args:
            obj (Object): The object on which the handler is defined.
        """
        self.obj = obj
        self._sessions = list()

    def all(self):
        """
        Returns all sessions.

        Returns:
            sessions (list): All sessions.
        """
        return list(self._sessions)

    def save(self):
        """
        Doesn't do anything on its own. Some things might want to store session ids in the database or something.
        There is no load. There will not be a load.
        """

    def add(self, session, force=False, sync=False, **kwargs):
        """
        Add session to handler. Do not call this directly - it is meant to be called from
        ServerConnection.link(). If this is called directly, ServerConnection will not set import attributes.

        Args:
            session (Connection or int): Connection or session id to add.
            force (bool): Don't stop for anything. Mainly used for Unexpected Disconnects
            sync (bool):

        Returns:
            result (bool): True if success, false if fail.

        Notes:
            We will only add a session/sessid if this actually also exists
            in the core connectionhandler.
        """
        try:
            if session in self._sessions:
                raise ValueError("Connection is already linked to this entity!")
            self.validate_link_request(self, sync, **kwargs)
        except ValueError as e:
            session.msg(e)
            return False
        self.at_before_link_session(self, session, force=force, sync=sync, **kwargs)
        self._sessions.append(session)
        self.at_link_session(self, session, force=force, sync=sync, **kwargs)
        self.at_after_link_session(self, session, force=force, sync=sync, **kwargs)

        # I really don't know why, but ObjectDB loves to save stuff.
        self.save()
        return True

    def remove(self, session, force=False, reason=None, **kwargs):
        """
        Remove session from handler. As with add(), it must be called by ServerConnection.unlink().

        Args:
            session (Connection or int): Connection or session id to remove.
            force (bool): Don't stop for anything. Mainly used for Unexpected Disconnects
            reason (str or None): A reason that might be displayed down the chain.
        """
        try:
            if session not in self._sessions:
                raise ValueError("Cannot remove session: it is not linked to this object.")
            self.validate_unlink_request(self, force=force, reason=reason, **kwargs)
        except ValueError as e:
            self.msg(e)
            return
        self.at_before_unlink_session(self, force=force, reason=reason, **kwargs)
        self._sessions.remove(session)
        self.at_unlink_session(self, force=force, reason=reason, **kwargs)
        self.at_after_unlink_session(self, force=force, reason=reason, **kwargs)

        # I really don't know why, but ObjectDB loves to save stuff.
        self.save()
        return True

    def count(self):
        """
        Get amount of sessions connected.
        Returns:
            sesslen (int): Number of sessions handled.
        """
        return len(self._sessions)

    def validate_link_request(self, session, force=False, sync=False, **kwargs):
        """
        This is called to check if a Connection should be allowed to link this entity.

        Args:
            session (ServerConnection): The Connection in question.
            force (bool): Bypass most checks for some reason? Usually admin overrides.
            sync (bool): Whether this is operating in sync-after-reload mode.
                In general, nothing should stop it if this is true.

        Raises:
            ValueError(str): An error condition which will prevent the linking.
        """
        raise NotImplementedError()

    def at_before_link_session(self, session, force=False, sync=False, **kwargs):
        """
        This is called to ready an entity for linking. This might do cleanups, kick
        off other Sessions, whatever it needs to do.

        Args:
            session (ServerConnection): The Connection in question.
            force (bool): Bypass most checks for some reason? Usually admin overrides.
            sync (bool): Whether this is operating in sync-after-reload mode.
                In general, nothing should stop it if this is true.
        """
        raise NotImplementedError()

    def at_link_session(self, session, force=False, sync=False, **kwargs):
        """"
        Sets up our Connection connection.
        Args:
            session (ServerConnection): The Connection in question.
            force (bool): Bypass most checks for some reason? Usually admin overrides.
            sync (bool): Whether this is operating in sync-after-reload mode.
                In general, nothing should stop it if this is true.
        """
        raise NotImplementedError()

    def at_after_link_session(self, session, force=False, sync=False, **kwargs):
        """
        Called just after puppeting has been completed and all
        Account<->Object links have been established.
        Args:
            session (ServerConnection): The Connection in question.
            force (bool): Bypass most checks for some reason? Usually admin overrides.
            sync (bool): Whether this is operating in sync-after-reload mode.
                In general, nothing should stop it if this is true.
        Note:
            You can use `self.account` and `self.sessions.get()` to get
            account and sessions at this point; the last entry in the
            list from `self.sessions.get()` is the latest Connection
            puppeting this Object.
        """
        raise NotImplementedError()

    def validate_unlink_request(self, session, force=False, reason=None, **kwargs):
        """
        Validates an unlink. This can halt an unlink for whatever reason.

        Args:
            session (ServerConnection): The session that will be leaving us.
            force (bool): Don't stop for anything. Mainly used for Unexpected Disconnects
            reason (str or None): A reason that might be displayed down the chain.

        Raises:
            ValueError(str): If anything is amiss, raising ValueError will block the
                unlink.
        """
        raise NotImplementedError()

    def at_before_unlink_session(self, session, force=False, reason=None, **kwargs):
        """
        Called just before beginning to un-connect a puppeting from
        this Account.
        Args:
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        Note:
            You can use `self.account` and `self.sessions.get()` to get
            account and sessions at this point; the last entry in the
            list from `self.sessions.get()` is the latest Connection
            puppeting this Object.
        """
        raise NotImplementedError()

    def at_unlink_session(self, session, force=False, reason=None, **kwargs):
        """
        That's all folks. Disconnect session from this object.

        Args:
            session (ServerConnection): The session that will be leaving us.
            force (bool): Don't stop for anything. Mainly used for Unexpected Disconnects
            reason (str or None): A reason that might be displayed down the chain.
        """
        raise NotImplementedError()

    def at_after_unlink_session(self, session, force=False, reason=None, **kwargs):
        """
        Called just after the Account successfully disconnected from
        this object, severing all connections.
        Args:
            account (Account): The account object that just disconnected
                from this object.
            session (Connection): Connection id controlling the connection that
                just disconnected.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        raise NotImplementedError()


class AccountSessionHandler(EntitySessionHandler):

    def validate_link_request(self, session, force=False, sync=False, **kwargs):
        """
        Nothing really to do here. Accounts are validated through their password. That's .authenticate().
        """

    def at_before_link_session(self, session, force=False, sync=False, **kwargs):
        existing = self.all()
        if settings.MULTISESSION_MODE == 0:
            # disconnect all previous sessions.
            # session.connectionhandler.disconnect_duplicate_sessions(session)
            pass  # I will make this work later

    def at_link_session(self, session, force=False, sync=False, **kwargs):
        session.logged_in = True
        session.uname = self.obj.name
        session.uid = self.obj.pk
        session.conn_time = time.time()
        session.cmdset.add(settings.CMDSET_SESSION, permanent=True, default_cmdset=True)

    def at_after_link_session(self, session, force=False, sync=False, **kwargs):
        self.obj.at_init()
        # Check if this is the first time the *account* logs in
        if self.obj.db.FIRST_LOGIN:
            self.obj.at_first_login()
            del self.obj.db.FIRST_LOGIN
        self.obj.last_login = timezone.now()
        self.obj.save()
        nsess = self.count()
        session.log(f"Logged in: {self} {session.address} ({nsess} session(s) total)")
        if nsess < 2:
            pass

        #    SIGNAL_ACCOUNT_POST_FIRST_LOGIN.send(sender=self, session=session)
        #  SIGNAL_ACCOUNT_POST_LOGIN.send(sender=self, session=session)

    def validate_unlink_request(self, session, force=False, reason=None, **kwargs):
        pass

    def at_before_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass

    def at_unlink_session(self, session, force=False, reason=None, **kwargs):
        session.logged_in = False
        session.uid = None
        session.uname = None
        session.cmdset.add(settings.CMDSET_UNLOGGEDIN, permanent=True, default_cmdset=True)

    def at_after_unlink_session(self, session, force=False, reason=None, **kwargs):
        if not (remaining := self.all()):
            self.obj.attributes.add(key="last_active_datetime", category="system", value=timezone.now())
            self.obj.is_connected = False
        MONITOR_HANDLER.remove(self.obj, "_saved_webclient_options", session.sessid)

        session.log(f"Logged out: {self.obj} {session.address} ({len(remaining)} sessions(s) remaining)"
                    f"{reason if reason else ''}")

        if not remaining:
            pass
            # SIGNAL_ACCOUNT_POST_LAST_LOGOUT.send(sender=session.account, session=session)
        # SIGNAL_ACCOUNT_POST_LOGOUT.send(sender=session.account, session=session)
        sessid = session.sessid


class PuppetSessionHandler(EntitySessionHandler):

    def validate_link_request(self, session, force=False, sync=False, **kwargs):
        if not (account := session.get_account()):
            # not logged in. How did this even happen?
            raise ValueError("You are not logged in to an account!")
        if not self.obj.access(account, "puppet"):
            # no access
            raise ValueError(f"You don't have permission to puppet '{self.obj.key}'.")
        if (me_account := session.get_account()) and me_account != account:
            raise ValueError(f"|c{self.obj.key}|R is already puppeted by another Account.")

    def at_before_link_session_unstow(self, session, force=False, sync=False, **kwargs):
        """
        Some things are kept in null-space or alternate locations. Use this hook for relocating
        an object before it is puppeted.
        """
        pass

    def at_before_link_session(self, session, force=False, sync=False, **kwargs):
        pass

    def at_link_session(self, session, force=False, sync=False, **kwargs):
        session.puid = self.obj.pk
        session.puppet = self

        # Don't need to validate scripts if there already were sessions attached.
        if not self.count() > 1:
            self.obj.scripts.validate()

        if sync:
            self.obj.locks.cache_lock_bypass(self)

    def at_after_link_session_message(self, session, force=False, sync=False, **kwargs):
        """
        Used for sending messages announcing that you have connected. Maybe to you?
        Maybe to people in the same location?
        """
        self.obj.msg(f"You become |w{self.obj.key}|n.")

    def at_after_link_session(self, session, force=False, sync=False, **kwargs):
        session.account.db._last_puppet = self

    def validate_unlink_request(self, session, force=False, reason=None, **kwargs):
        pass

    def at_before_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass

    def at_unlink_session(self, session, force=False, reason=None, **kwargs):
        session.puid = None
        session.puppet = None

    def at_after_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass


class CharacterSessionHandler(EntitySessionHandler):

    def validate_link_request(self, session, force=False, sync=False, **kwargs):
        pass

    def at_before_link_session_multisession(self, session, force=False, sync=False, **kwargs):
        """
        Multisession logic is performed here. This should not stop the link process.
        """
        # object already puppeted
        # we check for whether it's the same account in a _validate_puppet_request.
        # if we reach here, assume that it's either no account or the same account
        if (others := self.all()):
            # we may take over another of our sessions
            # output messages to the affected sessions
            if settings.MULTISESSION_MODE in (1, 3):
                txt1 = f"Sharing |c{self.obj.name}|n with another of your sessions."
                txt2 = f"|c{self.obj.name}|n|G is now shared from another of your sessions.|n"
                session.msg(txt1)
                self.obj.msg(txt2, session=others)
            else:
                txt1 = f"Taking over |c{self.obj.name}|n from another of your sessions."
                txt2 = f"|c{self.obj.name}|n|R is now acted from another of your sessions.|n"
                session.msg(txt1)
                self.obj.msg(txt2, session=others)
                for other in others:
                    other.unlink('puppet', self, force=True, reason="Taken over by another session")

    def at_before_link_session(self, session, force=False, sync=False, **kwargs):
        # First, check multisession status. Kick off anyone as necessary.
        self.at_before_link_session_multisession(session, force, sync, **kwargs)
        # Next, call the hook for object relocation.
        self.at_before_link_session_unstow(session, force, sync, **kwargs)

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
