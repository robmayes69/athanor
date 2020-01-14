"""
Core of the Athanor API.

"""
from collections import defaultdict

PLUGINS = dict()

CMDSETS = defaultdict(list)

SETTINGS = dict()

_LIST_SETTINGS = ("SERVER_SERVICES_PLUGIN_MODULES", "PORTAL_SERVICES_PLUGIN_MODULES", "INSTALLED_APPS",
                  "LOCK_FUNC_MODULES", "INPUT_FUNC_MODULES", "INLINEFUNC_MODULES", "PROTOTYPE_MODULES",
                  "PROTOTYPEFUNC_MODULES", "PROT_FUNC_MODULES", "CMDSET_PATHS", "TYPECLASS_PATHS",
                  "OPTION_CLASS_MODULES", "VALIDATOR_FUNC_MODULES", "BASE_BATCHPROCESS_PATHS",
                  "STATICFILES_DIRS")

_CMDSET_SETTINGS = ("CMDSETS_ACCOUNT", "CMDSETS_CHARACTER", "CMDSETS_LOGIN", "CMDSETS_SESSION")

_DICT_SETTINGS = ("GLOBAL_SCRIPTS", "OPTIONS_ACCOUNT_DEFAULT")


def _init(plugin_paths, plugin_class_path):
    from evennia.utils.utils import class_from_module
    global PLUGINS, _LIST_SETTINGS, _DICT_SETTINGS, SETTINGS, CMDSETS

    plugin_class = class_from_module(plugin_class_path)

    for plugin_path in plugin_paths:
        plugin = plugin_class(class_from_module(plugin_path))
        plugin.initialize()
        PLUGINS[plugin.key] = plugin

        for op in _LIST_SETTINGS:
            if op not in SETTINGS:
                SETTINGS[op] = list()
            SETTINGS[op].extend(plugin.get_setting(op, list()))

        for op in _DICT_SETTINGS:
            if op not in SETTINGS:
                SETTINGS[op] = dict()
            SETTINGS[op].update(plugin.get_setting(op, dict()))

        for op in _CMDSET_SETTINGS:
            CMDSETS[op].extend(plugin.get_setting(op, list()))

    all_cmdsets = dict()
    for cmdset_category in _CMDSET_SETTINGS:
        cmdsets = list()
        for cmdset_path in CMDSETS[cmdset_category]:
            cmdsets.append(class_from_module(cmdset_path))
        all_cmdsets[cmdset_category] = cmdsets
    CMDSETS = all_cmdsets
