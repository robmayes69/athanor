from evennia.typeclasses.models import TypeclassBase
from evennia.objects.objects import ObjectSessionHandler
from evennia.utils.utils import lazy_property, logger, make_iter, to_str

from athanor.playtimes.models import PlaytimeDB
from athanor.playtimes.handlers import PlaytimeCmdSetHandler


class DefaultPlaytime(PlaytimeDB, metaclass=TypeclassBase):

    @lazy_property
    def cmdset(self):
        return PlaytimeCmdSetHandler(self)

    @lazy_property
    def sessions(self):
        return ObjectSessionHandler(self)

    def at_msg_receive(self, text=None, from_obj=None, **kwargs):
        """
        See evennia.objects.objects.DefaultObject's at_msg_receive()
        """
        return True

    def msg(self, text=None, from_obj=None, session=None, options=None, **kwargs):
        """
        See evennia.objects.objects.DefaultObject's .msg()
        """
        # try send hooks
        if from_obj:
            for obj in make_iter(from_obj):
                try:
                    obj.at_msg_send(text=text, to_obj=self, **kwargs)
                except Exception:
                    logger.log_trace()
        kwargs["options"] = options
        try:
            if not self.at_msg_receive(text=text, **kwargs):
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

        # relay to session(s)
        sessions = make_iter(session) if session else self.sessions.all()
        for session in sessions:
            session.data_out(**kwargs)

    def at_first_save(self):
        pass

    def at_cmdset_get(self, **kwargs):
        pass

