"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    import athanor
    athanor.LOADER.load_found()
    athanor.LOADER.load_final()
    athanor.LOADER.load_systems()
    for m in athanor.LOADER.modules_order:
        if hasattr(m, 'at_server_start'):
            m.at_server_start()


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    import athanor
    for m in athanor.LOADER.modules_order:
        if hasattr(m, 'at_server_stop'):
            m.at_server_stop()


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    import athanor
    for m in athanor.LOADER.modules_order:
        if hasattr(m, 'at_server_reload_start'):
            m.at_server_reload_start()


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    import athanor
    for m in athanor.LOADER.modules_order:
        if hasattr(m, 'at_server_reload_stop'):
            m.at_server_reload_stop()


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    import athanor
    for m in athanor.LOADER.modules_order:
        if hasattr(m, 'at_server_cold_start'):
            m.at_server_cold_start()
    for s in athanor.LOADER.systems.values():
        s.at_server_cold_start()


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    import athanor
    for m in athanor.LOADER.modules_order:
        if hasattr(m, 'at_server_cold_stop'):
            m.at_server_cold_stop()
