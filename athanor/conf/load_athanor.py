"""
Athanor Core module's Server loader. This is responsible for readying Athanor! It will load all
classes, validators, handlers, managers, etc, retrieving their actual objects from Python Paths.

Afterwards, the 'athanor' module will have all needed data to run.
"""


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    
    import importlib, athanor, traceback, sys
    from evennia.utils.utils import class_from_module
    from evennia.utils.create import create_script
    from athanor.utils.utils import import_property

    dicts = ('MANAGERS', 'HANDLERS_ACCOUNT', 'HANDLERS_CHARACTER', 'HANDLERS_SESSION', 'RENDERERS',
             'STYLES_ACCOUNT', 'STYLES_CHARACTER', 'STYLES_SESSION', 'STYLES_FALLBACK', 'VALIDATORS',
             'SYSTEMS')

    for module in athanor.MODULES_ORDER:
        # First, we have to update all of the dictionaries based on their load order.
        for prop in dicts:
            if hasattr(module, prop):
                getattr(athanor, prop).update(getattr(module, prop))

    # Now that all of the modules dictionary key-values are present, load objects and classes!
    for prop in dicts:
        loading = getattr(athanor, prop)
        for k, v in loading.iteritems():
            loading[k] = import_property(v)

    # Now, all validators, managers, handlers, styles, etc, should all be references to their
    # actual Python data instead of just python path strings.

    # Next step: instantiate Systems from their Script Typeclasses.

    for key, system in athanor.SYSTEMS.iteritems():
        found = system.objects.filter_family(db_key=key).first()
        if found:
            athanor.SYSTEMS[key] = found
        else:
            athanor.SYSTEMS[key] = create_script(system, key=key, persistent=True, interval=60)

    # Lastly, if any module implements its own custom install process, we'll call that.
    for plugin in athanor.MODULES_ORDER:
        if hasattr(plugin, 'setup_module'):
            plugin.setup_module()


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    pass


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    pass


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass
