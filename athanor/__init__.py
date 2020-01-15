"""
Core of the Athanor API.

"""
from collections import defaultdict

PLUGINS = list()

CMDSETS = defaultdict(list)

SETTINGS = dict()

MIXINS = dict()

_LIST_SETTINGS = ("SERVER_SERVICES_PLUGIN_MODULES", "PORTAL_SERVICES_PLUGIN_MODULES", "INSTALLED_APPS",
                  "LOCK_FUNC_MODULES", "INPUT_FUNC_MODULES", "INLINEFUNC_MODULES", "PROTOTYPE_MODULES",
                  "PROTOTYPEFUNC_MODULES", "PROT_FUNC_MODULES", "CMDSET_PATHS", "TYPECLASS_PATHS",
                  "OPTION_CLASS_MODULES", "VALIDATOR_FUNC_MODULES", "BASE_BATCHPROCESS_PATHS",
                  "STATICFILES_DIRS")

_CMDSET_SETTINGS = ("CMDSETS_ACCOUNT", "CMDSETS_CHARACTER", "CMDSETS_LOGIN", "CMDSETS_SESSION")

_DICT_SETTINGS = ("GLOBAL_SCRIPTS", "OPTIONS_ACCOUNT_DEFAULT")


def _init(plugin_paths):
    from importlib import import_module
    global PLUGINS, _LIST_SETTINGS, _DICT_SETTINGS, SETTINGS, CMDSETS

    for plugin_path in plugin_paths:
        plugin_module = import_module(plugin_path)
        PLUGINS.append(plugin_module)

        for op in _LIST_SETTINGS:
            if op not in SETTINGS:
                SETTINGS[op] = list()
            SETTINGS[op].extend(getattr(plugin_module, op, list()))

        for op in _DICT_SETTINGS:
            if op not in SETTINGS:
                SETTINGS[op] = dict()
            SETTINGS[op].update(getattr(plugin_module, op, dict()))

        for op in _CMDSET_SETTINGS:
            CMDSETS[op].extend(getattr(plugin_module, op, list()))
