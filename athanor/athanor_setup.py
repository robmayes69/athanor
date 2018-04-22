
# Core setup stuff below. Don't touch this.
plugins = dict()
load_order = list()
start_stop = list()
initial_setup = list()

handler_classes = {
    'account': tuple(),
    'character': tuple(),
    'script': tuple(),
    'session': tuple(),
}

style_classes = {
    'account': tuple(),
    'character': tuple(),
}

system_scripts = dict()

system_classes = dict()

valid = dict()

def setup(module_list):
    import importlib
    global plugins, load_order, initial_setup, start_stop
    for plugin in module_list:
        load_plugin = importlib.import_module('%s.athanor_plugin' % plugin)
        plugins[plugin] = load_plugin

    load_order = sorted(plugins.values(), key=lambda m: m.LOAD_ORDER)

    for plugin in load_order:
        if hasattr(plugin, 'INITIAL_SETUP'):
            initial_setup += plugin.INITIAL_SETUP
        if hasattr(plugin, 'START_STOP'):
            start_stop += plugin.START_STOP
