"""
Core of the Athanor API.

"""


def load(settings):

    from importlib import import_module

    plugins = list()
    for plugin_path in settings.ATHANOR_PLUGINS:
        plugin_module = import_module(plugin_path)
        plugins.append(plugin_module)
    plugins.sort(key=lambda x: getattr(x, "LOAD_PRIORITY", 0))

    for plugin in plugins:
        if hasattr(plugin, "load"):
            plugin.load(settings)

    settings.ATHANOR_PLUGINS_LOADED.extend(plugins)