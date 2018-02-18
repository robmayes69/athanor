from __future__ import unicode_literals
import evennia

def sessions():
    """
    Simple shortcut to retrieving all connected sessions.

    Returns:
        list
    """
    return evennia.SESSION_HANDLER.values()


def accounts():
    """
    Uses the current online sessions to derive a list of connected players.

    Returns:
        list
    """
    from athanor.classes.accounts import Account
    return sorted([player for player in evennia.SESSION_HANDLER.all_connected_players()
            if player.is_typeclass(Account, exact=False)], key=lambda play: play.key)

def characters():
    """
    Uses the current online sessions to derive a list of connected characters.

    Returns:
        list
    """
    from athanor.classes.characters import Character as chr
    characters = [session.get_puppet() for session in sessions() if session.get_puppet()]
    characters = [char for char in characters if char.is_typeclass(chr, exact=False)]
    return sorted(list(set(characters)), key=lambda char: char.key)