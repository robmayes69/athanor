"""
Core of the Athanor API.

"""
CONTROLLER_MANAGER = None

STYLER = None


def load(settings):

    from importlib import import_module

    plugins = list()
    for plugin_path in settings.ATHANOR_PLUGINS:
        plugin_module = import_module(plugin_path)
        plugins.append(plugin_module)
    plugins.sort(key=lambda x: getattr(x, "LOAD_PRIORITY", 0))

    for plugin in plugins:
        if hasattr(plugin, "init_settings"):
            plugin.init_settings(settings)

    settings.ATHANOR_PLUGINS_LOADED.extend(plugins)