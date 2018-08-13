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

    import athanor, sys, traceback
    from athanor.utils.utils import import_property
    try:

        dicts = ('MANAGERS', 'HANDLERS_ACCOUNT', 'HANDLERS_CHARACTER', 'HANDLERS_SESSION',
                'VALIDATORS', 'SETTINGS',
                 'SYSTEMS', 'HELP_TREES', 'HELP_FILES', 'SHELP_FILES', 'PROPERTIES_ACCOUNT', 'PROPERTIES_CHARACTER',
                 'PROPERTIES_SESSION')

        for module in athanor.MODULES_ORDER:
            # First, we have to update all of the dictionaries based on their load order.
            for prop in dicts:
                if hasattr(module, prop):
                    getattr(athanor, prop).update(getattr(module, prop))

        # Now that all of the modules dictionary key-values are present, load objects and classes!
        for prop in dicts:
            if prop in ('HELP_TREES', 'HELP_FILES', 'SHELP_FILES'):
                continue
            loading = getattr(athanor, prop)
            for k, v in loading.iteritems():
                loading[k] = import_property(v)

        # Now, all validators, managers, handlers, styles, etc, should all be references to their
        # actual Python data instead of just python path strings.

        # Load all of the PROPERTY Getters into the Dictionary for them!
        for k, d in (('account', 'PROPERTIES_ACCOUNT'), ('character', 'PROPERTIES_CHARACTER'),
                     ('session', 'PROPERTIES_SESSION'), ('script', 'PROPERTIES_SCRIPT')):
            props = getattr(athanor, d)
            athanor.PROPERTIES_DICT[k] = props

        # Sort all of the Handlers into the appropriate dictionary so that managers load faster.

        for k, d in (('account', 'HANDLERS_ACCOUNT'), ('character', 'HANDLERS_CHARACTER'),
                     ('session', 'HANDLERS_SESSION'), ('script', 'HANDLERS_SCRIPT')):
            handlers = getattr(athanor, d).values()
            handlers.sort(key=lambda h: h.load_order)
            athanor.HANDLERS_SORTED[k] = tuple(handlers)

        # Next step: instantiate Systems from their Classes.

        from evennia import create_script
        for system in sorted(athanor.SYSTEMS.values(), key=lambda s: s.load_order):
            key = system.key
            found = system.objects.filter_family(db_key=key).first()
            if found:
                if not found.is_typeclass(system, exact=True):
                    found.swap_typeclass(system)
                if not found.interval == system.run_interval:
                    found.restart(interval=system.run_interval)
                athanor.SYSTEMS[key] = found
            else:
                athanor.SYSTEMS[key] = create_script(key=key, interval=system.run_interval, persistent=True, typeclass=system)

        for help, data in athanor.HELP_TREES.iteritems():
            files = data[1].values()
            root = import_property(data[0])(sub_files=files)
            athanor.HELP_TREES[help] = root

        # Lastly, if any module implements its own custom install process, we'll call that.
        for plugin in athanor.MODULES_ORDER:
            if hasattr(plugin, 'setup_module'):
                plugin.setup_module()

    except:
        traceback.print_exc(file=sys.stdout)

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
