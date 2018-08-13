
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
    from athanor.accounts.classes import Account
    return sorted([acc for acc in evennia.SESSION_HANDLER.all_connected_accounts()
            if acc.is_typeclass(Account, exact=False)], key=lambda acc: acc.key)

def characters():
    """
    Uses the current online sessions to derive a list of connected characters.

    Returns:
        list
    """
    from athanor.characters.classes import Character as chr
    characters = [session.get_puppet() for session in sessions() if session.get_puppet()]
    characters = [char for char in characters if char.is_typeclass(chr, exact=False)]
    return sorted(list(set(characters)), key=lambda char: char.key)

def admin():
    """
    Filters characters() by who counts as an admin!
    Also returns online accounts who are admin and have no characters logged in.

    :return: list
    """
    return [char for char in characters() if char.ath['core'].is_admin()]
