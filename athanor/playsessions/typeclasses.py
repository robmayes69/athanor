from django.conf import settings
from evennia.utils.utils import lazy_property
from athanor.identities.typeclasses import AthanorIdentityScript
from athanor.playsessions.handlers import PlaySessionCmdHandler, PlaySessionCmdSetHandler, PlaySessionSessionHandler


class AthanorPlaySession(AthanorIdentityScript):
    """
    A PlaySession represents a PlayerCharacter's in-game activities. Although this could be
    tracked as just 'an active PlayerCharacter' (running Script, as opposed to a paused one), having a
    PlaySession allows for a level of separation between the ongoing state of play and the character
    data. Menu CmdSets, for instance, should target the PlaySession.

    A PlaySession .stop()'ing is termination of the PlaySession. This should handle all cleanups.
    Although most games might have a PlaySession be only in existence for as long as there are
    active connections (losing all connections perhaps triggering a timeout after X intervals?),
    nothing prevents a PlaySession from lasting indefinitely.

    Multiple ServerSessions (connections) can share a PlaySession if they all select the same
    PlayerCharacter.

    The number of PlaySessions-per-Account can be configured in settings too.
    """
    _verbose_name = 'PlaySession'
    _verbose_name_plural = "PlaySessions"
    _namespace = 'playsessions'
    _re_name = None
    _cmd_sort = 10
    _default_cmdset = settings.CMDSET_PLAYSESSION

    @lazy_property
    def cmdset(self):
        return PlaySessionCmdSetHandler(self, True)

    @lazy_property
    def cmd(self):
        return PlaySessionCmdHandler(self)

    @lazy_property
    def sessions(self):
        return PlaySessionSessionHandler(self)

    def at_logout(self, forced=False, unexpected=False, reason=None):
        """
        This hook is called when the PlaySession must come to an end. At this point, nothing
        can stop the process. This
        Args:
            forced (bool): This logout is forced. This is likely because of some system event such as
                being banned, authentication expiry, an admin terminated the session, or the server is
                shutting down.
            unexpected (bool): This logout was not expected. This is usually in the case of a timeout
                (all ServerSessions lost connection without going through a proper logout process.)
            reason (str): The specific reason to display.
        """
        pass

    @classmethod
    def create_playsession(cls, player_character, **kwargs):
        account = player_character.get_account()
        kwargs['account'] = account
        kwargs['autostart'] = False
        kwargs['interval'] = 10
        return cls.create_identity(f"{player_character}{player_character.dbref}", **kwargs)

    def get_player_character(self):
        return self.db.character
