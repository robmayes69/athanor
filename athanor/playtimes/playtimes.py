from django.conf import settings
from evennia.typeclasses.models import TypeclassBase
from evennia.objects.objects import ObjectSessionHandler
from evennia.utils.utils import lazy_property, logger, make_iter, to_str

from athanor.playtimes.models import PlaytimeDB
from athanor.playtimes.handlers import PlaytimeCmdSetHandler, PlaytimeCmdHandler


class DefaultPlaytime(PlaytimeDB, metaclass=TypeclassBase):

    @classmethod
    def create(cls, identity, account, alternate_puppet=None):
        char_obj = identity.wrapped
        if not char_obj:
            raise Exception("SOMETHING DONE GOOFED!")
        if not alternate_puppet:
            alternate_puppet = char_obj
        ptime = cls(db_identity=identity, db_account=account, db_primary_puppet=char_obj,
                    db_current_puppet=alternate_puppet, db_cmdset_storage=settings.CMDSET_PLAYTIME)
        ptime.save()
        return ptime

    def get_identity(self):
        return self.db_identity

    def get_playtime(self):
        return self

    @lazy_property
    def cmdset(self):
        return PlaytimeCmdSetHandler(self, True)

    @lazy_property
    def cmd(self):
        return PlaytimeCmdHandler(self)

    @lazy_property
    def sessions(self):
        return ObjectSessionHandler(self)

    def at_msg_receive(self, text=None, from_obj=None, puppet_obj=None, **kwargs):
        """
        See evennia.objects.objects.DefaultObject's at_msg_receive()
        """
        return True

    def at_first_save(self):
        pass

    def at_cmdset_get(self, **kwargs):
        pass

    def at_session_link(self, session, quiet):
        pass

    def at_playtime_start(self, session, quiet):
        """
        Called by the SerrverSession when its link_to_playtime is linking the very first Session to this Playtime.

        Use this hook to move Object-Puppets into the proper locations, trigger announcements, start scripts, etc.

        Args:
            session (ServerSession): The session that triggered this hook.
            quiet (bool): Whether this should be done quietly or not.
        """
        if self.db_primary_puppet != self.db_current_puppet:
            self.db_current_puppet.db._playtime = self
            self.db_current_puppet.db._primary_puppet = self.db_primary_puppet
            self.db_current_puppet.at_pre_puppet(self.db_account, session=session, quiet=quiet)
            self.db_current_puppet.at_post_puppet()
        self.db_primary_puppet.db._playtime = self
        self.db_primary_puppet.at_pre_puppet(self.db_account, session=session, quiet=quiet)
        self.db_primary_puppet.at_post_puppet()

    def at_session_unlink(self, quiet, graceful):
        """
        Called by the ServerSession when its unlink_from_playtime method has just cleared a Session from this
        Playtime.

        Args:
            quiet (bool): Whether that disconnection was done quietly for some reason.
            graceful (bool): If true, the disconnect was intentional and sanctioned by the system. If false, it occured
                due to something like an unexpectedly lost TCP connection.
        """

    def at_playtime_end(self, session, quiet, graceful):
        """
        Called by the ServerSession when its unlink_from_playtime method has just cleared the last Session from this
        Playtime.

        By default, this just calls at_playtime_cleanup(). However, the graceful toggle exists to implement
        more complex disconnection schemes.

        Args:
            session (ServerSession): The final ServerSession to disconnect.
            quiet (bool): Whether that disconnection was done quietly for some reason.
            graceful (bool): Whether this disconnection process is graceful. If not, some special scripts might
                be called. Perhaps character remain linkdead for X period of time?
        """
        self.at_playtime_cleanup(graceful)

    def at_playtime_cleanup(self, graceful: bool = True):
        """
        This should be the reverse of at_playtime_start. This should put Objects back into storage, set 'disconnected'
        flags, whatever.

        This should always leave the database in a consistent state, so be careful when writing it.

        Args:
            graceful (bool): Whether this is a graceful cleanup. This might affect messaging or setting flags.
        """
        if self.db_primary_puppet != self.db_current_puppet:
            del self.db_current_puppet.db._playtime
            del self.db_current_puppet.db._primary_puppet
            self.db_current_puppet.at_pre_unpuppet()
            self.db_current_puppet.at_post_unpuppet(self.db_account, session=self)
        del self.db_primary_puppet.db._playtime
        self.db_primary_puppet.at_pre_unpuppet()
        self.db_primary_puppet.at_post_unpuppet(self.db_account, session=self)

    def msg(self, text=None, from_obj=None, puppet_obj=None, session=None, options=None, **kwargs):
        """
        See evennia.objects.objects.DefaultObject's .msg() for reference.

        This distributes a msg received from a puppet to all linked Sessions.

        Args:
            session (ServerSession): This is ignored.
            puppet_obj (Object): The specific Object that this Playtime is receiving a message from.
            Rest, same as Object.msg()
        """
        if not (sessions := self.sessions.all()):
            # no reason to do anything if nobody's listening...
            return
        kwargs["options"] = options

        try:
            if not self.at_msg_receive(text=text, from_obj=from_obj, puppet_obj=puppet_obj, **kwargs):
                # if at_msg_receive returns false, we abort message to this object
                return
        except Exception:
            logger.log_trace()

        if text is not None:
            if not (isinstance(text, str) or isinstance(text, tuple)):
                # sanitize text before sending across the wire
                try:
                    text = to_str(text)
                except Exception:
                    text = repr(text)
            kwargs["text"] = text

        for session in sessions:
            session.data_out(**kwargs)

    @property
    def is_superuser(self):
        return (
                self.db_account
                and self.db_account.is_superuser
                and not self.db_account.attributes.get("_quell")
        )

    def __str__(self):
        return f"Playtime: {str(self.db_identity)}"
