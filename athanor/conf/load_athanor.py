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
    import importlib, athanor, traceback, sys
    from evennia.utils.utils import class_from_module
    from evennia.utils.create import create_script

    handlers_account = dict()
    handlers_character = dict()
    handlers_session = dict()
    handlers_script = dict()

    styles_account = dict()
    styles_character = dict()

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

    for plugin in athanor.load_order:
        try:
            # Retrieve validators!
            if hasattr(plugin, 'VALIDATORS'):
                for path in plugin.VALIDATORS:
                    val_mod = importlib.import_module(path)
                    athanor.valid.update(val_mod.ALL)

            # Retrieve Handlers!

            if hasattr(plugin, 'HANDLERS_ACCOUNT'):
                handlers_account.update(plugin.HANDLERS_ACCOUNT)

            if hasattr(plugin, 'HANDLERS_CHARACTER'):
                handlers_character.update(plugin.HANDLERS_CHARACTER)

            if hasattr(plugin, 'HANDLERS_SESSION'):
                handlers_session.update(plugin.HANDLERS_SESSION)

            if hasattr(plugin, 'HANDLERS_SCRIPT'):
                handlers_script.update(plugin.HANDLERS_SCRIPT)

            # Retrieve Styles!
            if hasattr(plugin, 'STYLES_ACCOUNT'):
                styles_account.update(plugin.STYLES_CHARACTER)

            if hasattr(plugin, 'STYLES_CHARACTER'):
                styles_character.update(plugin.STYLES_CHARACTER)

            # Retrieve Systems!
            if hasattr(plugin, 'SYSTEM_SCRIPTS'):
                system_scripts.update(plugin.SYSTEM_SCRIPTS)
        except:
            traceback.print_exc(file=sys.stdout)

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

    for mode, mode_dict in (('account',handlers_account), ('character', handlers_character), ('script', handlers_script), ('session', handlers_session)):
        for module in mode_dict.values():
            handler_classes[mode].append(class_from_module(module))
            handler_classes[mode].sort(key=lambda c: c.load_order)
            athanor.handler_classes[mode] = tuple(handler_classes[mode])


    for mode in ('account', 'character'):
        for module in styles[mode]:
            load_mod = importlib.import_module(module)
            style_classes[mode] += load_mod.ALL
            athanor.style_classes[mode] = tuple(style_classes[mode])

    for key in system_classes.keys():
        athanor.system_classes[key] = class_from_module(system_classes[key])

    for key in system_scripts:
        typeclass = class_from_module(system_scripts[key])
        found = typeclass.objects.filter_family(db_key=key).first()
        if found:
            athanor.system_scripts[key] = found
        else:
            athanor.system_scripts[key] = create_script(typeclass, key=key, persistent=True)

    for plugin in athanor.load_order:
        if hasattr(plugin, 'setup_plugin'):
            plugin.setup_plugin()


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
