""""""
from evennia.server.inputfuncs import _IDLE_COMMAND


# Renamed to text2 to 'disable' it for the moment.
def text(session, *args, **kwargs):
    """
    Main text input from the client. This will execute a command
    string on the server.

    Args:
        session (Session): The active Session to receive the input.
        text (str): First arg is used as text-command input. Other
            arguments are ignored.

    """
    # from evennia.server.profiling.timetrace import timetrace
    # text = timetrace(text, "ServerSession.data_in")

    txt = args[0] if args else None

    # explicitly check for None since text can be an empty string, which is
    # also valid
    if txt is None:
        return
    # this is treated as a command input
    # handle the 'idle' command
    if txt.strip() in _IDLE_COMMAND:
        session.update_session_counters(idle=True)
        return
    #TODO: fix this!
    #txt = session.cmd_nick_replace(txt)

    kwargs.pop("options", None)
    # This is the only change - call the session.cmd.execute() instead of cmdhandler(session...)
    session.cmd.execute(txt, session=session, **kwargs)
    session.update_session_counters()
