"""
Core of the Athanor API.

"""

def _init(settings):
    from importlib import import_module

    for plugin_path in settings.ATHANOR_PLUGINS:
        plugin_module = import_module(plugin_path)
        settings.ATHANOR_PLUGINS_LOADED.append(plugin_module)
        if hasattr(plugin_module, "_init"):
            plugin_module._init(settings)
