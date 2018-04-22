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
    import importlib
    from athanor import athanor_setup
    from evennia.utils.utils import class_from_module
    from evennia.utils.create import create_script
    
    handlers = {
        'account': list(),
        'character': list(),
        'script': list(),
        'session': list(),
    }
    
    styles = {
        'account': list(),
        'character': list(),
    }
    
    system_scripts = dict()
    
    system_classes = dict()

    for plugin in athanor_setup.load_order:

        # Retrieve validators!
        if hasattr(plugin, 'VALIDATORS'):
            for path in plugin.VALIDATORS:
                val_mod = importlib.import_module(path)
                athanor_setup.valid.update(val_mod.ALL)
    
        # Retrieve Handlers!
        if hasattr(plugin, 'HANDLERS'):
            for mode in ('account', 'character', 'script', 'session'):
                handlers[mode] += plugin.HANDLERS.get(mode, [])

        # Retrieve Styles!
        if hasattr(plugin, 'STYLES'):
            for mode in ('account', 'character'):
                styles[mode] += plugin.STYLES.get(mode, [])

        # Retrieve System Classes!
        if hasattr(plugin, 'SYSTEM_CLASSES'):
            system_classes.update(plugin.SYSTEM_CLASSES)

        # Retrieve Systems!
        if hasattr(plugin, 'SYSTEM_SCRIPTS'):
            system_scripts.update(plugin.SYSTEM_SCRIPTS)

        # Begin loading process.
    handler_classes = {
        'account': list(),
        'character': list(),
        'script': list(),
        'session': list(),
    }

    style_classes = {
        'account': list(),
        'character': list(),
    }
        
    system_class_classes = dict()
    system_script_classes = dict()
    print handlers
    for mode in ('account', 'character', 'script', 'session'):
        print "loading handlers %s" % mode
        for module in handlers[mode]:
            print "loading module %s" % module
            try:
                load_mod = importlib.import_module(module)
                print load_mod
            except Exception as err:
                print err
            print load_mod
            print load_mod.ALL
            handler_classes[mode] += load_mod.ALL
            handler_classes[mode].sort(key=lambda c: c.load_order)
            athanor_setup.handler_classes[mode] = tuple(handler_classes[mode])
    print athanor_setup.handler_classes
    print styles
    for mode in ('account', 'character'):
        for module in styles[mode]:
            load_mod = importlib.import_module(module)
            style_classes[mode] += load_mod.ALL
            style_classes[mode].sort(key=lambda c: c.load_order)
            athanor_setup.style_classes[mode] = tuple(style_classes[mode])
    print athanor_setup.style_classes
    for key in system_classes.keys():
        athanor_setup.system_classes[key] = class_from_module(system_classes[key])

    for key in system_scripts:
        typeclass = class_from_module(system_scripts[key])
        found = typeclass.objects.filter_family(db_key=key).first()
        if found:
            athanor_setup.system_scripts[key] = found
        else:
            athanor_setup.system_scripts[key] = create_script(typeclass, key=key, persistent=True)

    print handler_classes

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
