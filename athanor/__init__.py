"""
Core of the Athanor API. It is also styled as a plugin.

"""
from evennia.utils.utils import lazy_property

# This dictionary will be filled in with useful singletons as the system loads.

_API_STORAGE = dict()

# The Core must always load first.
LOAD_PRIORITY = -100000000

PLUGIN_NAME = 'athanor'


def plugin_initial_setup(api):
    pass


class AthanorApi:

    def __init__(self):
        self.storage = dict()
        pspace_dict = dict()

        from athanor.identities.models import Namespace

        def get_or_create_pspace(pspace):
            if pspace in pspace_dict:
                return pspace_dict[pspace]
            model, created = Pluginspace.objects.get_or_create(db_name=pspace)
            if created:
                model.save()
            pspace_dict[pspace] = model
            return model

        from django.conf import settings
        from evennia.utils.utils import class_from_module

        self.plugins = settings.ATHANOR_PLUGINS
        self.plugins_sorted = settings.ATHANOR_PLUGINS_SORTED

        for plugin in settings.ATHANOR_PLUGINS.keys():
            get_or_create_pspace(plugin)

        for namespaces in settings.IDENTITY_NAMESPACES:
            nspace, created = Namespace.objects.get_or_create(db_name=namespaces)
            if created:
                nspace.save()

        styler_class = class_from_module(settings.STYLER_CLASS)
        self.styler = styler_class
        self.styler.load()

        try:
            self.controllers = class_from_module(settings.CONTROLLER_MANAGER_CLASS)(self)
            self.controllers.load()

        except Exception as e:
            from evennia.utils import logger
            logger.log_trace(e)
            print(e)


@lazy_property
def api() -> AthanorApi:
    return AthanorApi()


def _init():
    global LOADED, _API_STORAGE
    if LOADED:
        return
    LOADED = True

    pspace_dict = dict()

    def get_or_create_pspace(pspace):
        if pspace in pspace_dict:
            return pspace_dict[pspace]
        model, created = Pluginspace.objects.get_or_create(db_name=pspace)
        if created:
            model.save()
        pspace_dict[pspace] = model
        return model

    from django.conf import settings
    from evennia.utils.utils import class_from_module

    from athanor.models import Pluginspace, Namespace

    for plugin in settings.ATHANOR_PLUGINS.keys():
        get_or_create_pspace(plugin)

    for namespaces in settings.IDENTITY_NAMESPACES:
        nspace, created = Namespace.objects.get_or_create(db_name=namespaces)
        if created:
            nspace.save()

    styler_class = class_from_module(settings.STYLER_CLASS)
    _API_STORAGE['styler'] = styler_class
    _API_STORAGE['styler'].load()

    try:
        manager = class_from_module(settings.CONTROLLER_MANAGER_CLASS)()
        _API_STORAGE['controller_manager'] = manager
        manager.load()

        # Setting this true so that integrity checks will not call _init() again.
        entity_con = manager.get('entity')
        entity_con.check_integrity()
    except Exception as e:
        from evennia.utils import logger
        logger.log_trace(e)
        print(e)


def api():
    global LOADED, _API_STORAGE
    if not LOADED:
        _init()
    return _API_STORAGE


def init_settings(settings):
    from collections import defaultdict

    ######################################################################
    # Server Options
    ######################################################################

    settings.SERVERNAME = "Athanor: Advent of Awesome"

    # Let's disable that annoying timeout by default!
    settings.IDLE_TIMEOUT = -1

    # A lot of MUD-styles may want to change this to 2. Athanor's not really meant for 0 or 1 style, though.
    settings.MULTISESSION_MODE = 3

    settings.USE_TZ = True
    settings.TELNET_OOB_ENABLED = True
    settings.WEBSOCKET_ENABLED = True
    settings.INLINEFUNC_ENABLED = True

    settings.AT_INITIAL_SETUP_HOOK_MODULE = "athanor.at_initial_setup"
    settings.AT_SERVER_STARTSTOP_MODULE = "athanor.at_server_startstop"
    settings.HELP_MORE = False
    settings.CONNECTION_SCREEN_MODULE = "athanor.connection_screens"
    settings.CMD_IGNORE_PREFIXES = ""

    # The Styler is an object that generates commonly-used formatting, like
    # headers and tables.
    settings.STYLER_CLASS = "athanor.utils.styling.Styler"

    # The EXAMINE HOOKS are used to generate Examine-styled output. It differs by types.
    settings.EXAMINE_HOOKS = defaultdict(list)
    settings.EXAMINE_HOOKS['object'] = ['object', 'puppeteer', 'access', 'commands', 'scripts', 'tags', 'attributes',
                                        'contents']

    # the CMDSETS dict is used to control 'extra cmdsets' our special CmdHandler divvies out.
    # the keys are the objdb that it applies to, such as 'account' or 'avatar'. This is separate
    # from the 'main' cmdset. It is done this way so that plugins can easily add extra cmdsets to
    # different entities.
    settings.CMDSETS = defaultdict(list)

    # Taking control of initial setup. No more screwy godcharacter nonsense.
    settings.INITIAL_SETUP_MODULE = "athanor.initial_setup"

    ######################################################################
    # Module List Options
    ######################################################################
    # Convert LOCK_FUNC_MODULES to a list so it can be appended to by plugins.
    settings.LOCK_FUNC_MODULES = list(settings.LOCK_FUNC_MODULES)
    settings.LOCK_FUNC_MODULES.append("athanor.lockfuncs")

    settings.INPUT_FUNC_MODULES.append('athanor.inputfuncs')

    ######################################################################
    # Database Options
    ######################################################################
    # convert INSTALLED_APPS to a list so that plugins may append to it.
    # At this point, we can only add things after Evennia's defaults.
    settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
    settings.INSTALLED_APPS.append('athanor')

    ######################################################################
    # Namespaces
    ######################################################################

    settings.IDENTITY_NAMESPACES = {
        "Special": {"sort": 0, "prefix": "S"},
        "Accounts": {"sort": 100, "prefix": "A"},
        "Characters": {"sort": 200, "prefix": "C"},
        "Factions": {"sort": 300, "prefix": "F"},
        "Themes": {"sort": 400, "prefix": "T"}
    }

    ######################################################################
    # Controllers
    ######################################################################

    settings.CONTROLLER_MANAGER_CLASS = "athanor.utils.controllers.ControllerManager"
    settings.BASE_CONTROLLER_CLASS = "athanor.utils.controllers.AthanorController"
    settings.CONTROLLERS = dict()


    ######################################################################
    # Grid/Map/Rooms Options
    ######################################################################
    # This is a mapping of 'shortcut' to (db_exit_key, [aliases]) for use with
    # layouts.
    settings.EXIT_MAP = {
        'n': ('north', ['n']),
        's': ('south', ['s']),
        'e': ('east', ['e']),
        'w': ('west', ['w']),
        'i': ('in', ['i']),
        'o': ('out', ['o']),
        'u': ('up', ['u']),
        'd': ('down', ['d']),
        'nw': ('northwest', ['nw']),
        'ne': ('northeast', ['ne']),
        'sw': ('southwest', ['sw']),
        'se': ('southeast', ['se'])
    }


    ######################################################################
    # Connection Options
    ######################################################################
    # Command set used on the logged-in session
    settings.CMDSET_SESSION = "athanor.cmdsets.session.AthanorSessionCmdSet"

    # Command set used on session before account has logged in
    settings.CMDSET_LOGINSCREEN = "athanor.serversessions.cmdsets.LoginCmdSet"
    settings.CMDSET_SELECTSCREEN = 'athanor.serversessions.cmdsets.CharacterSelectScreenCmdSet'
    settings.CMDSET_ACTIVE = 'athanor.serversessions.cmdsets.ActiveCmdSet'
    settings.BASE_SERVER_SESSION_TYPECLASS = "athanor.serversessions.serversessions.DefaultServerSession"
    settings.SERVER_SESSION_HANDLER_CLASS = 'athanor.utils.serversessionhandler.AthanorServerSessionHandler'

    settings.EXAMINE_HOOKS['session'] = []

    settings.SESSION_SYNC_ATTRS = list(settings.SESSION_SYNC_ATTRS)

    ######################################################################
    # Account Options
    ######################################################################
    settings.CONTROLLERS['account'] = {
        'class': 'athanor.accounts.controller.AthanorAccountController',
        'backend': 'athanor.accounts.controller.AthanorAccountControllerBackend'
    }

    settings.BASE_ACCOUNT_TYPECLASS = "athanor.accounts.typeclasses.AthanorAccount"

    # Command set for accounts with or without a character (ooc)
    settings.CMDSET_ACCOUNT = "athanor.accounts.cmdsets.AccountCmdSet"

    # Default options for display rules.
    settings.OPTIONS_ACCOUNT_DEFAULT['sys_msg_border'] = ('For -=<>=-', 'Color', 'm')
    settings.OPTIONS_ACCOUNT_DEFAULT['sys_msg_text'] = ('For text in sys_msg', 'Color', 'w')
    settings.OPTIONS_ACCOUNT_DEFAULT['border_color'] = ("Headers, footers, table borders, etc.", "Color", "M")
    settings.OPTIONS_ACCOUNT_DEFAULT['header_star_color'] = ("* inside Header lines.", "Color", "m")
    settings.OPTIONS_ACCOUNT_DEFAULT['header_text_color'] = ("Text inside Headers.", "Color", "w")
    settings.OPTIONS_ACCOUNT_DEFAULT['column_names_color'] = ("Table column header text.", "Color", "G")

    # If these are true, only admin can change these once they're set.
    settings.RESTRICTED_ACCOUNT_RENAME = False
    settings.RESTRICTED_ACCOUNT_EMAIL = False
    settings.RESTRICTED_ACCOUNT_PASSWORD = False

    settings.EXAMINE_HOOKS['account'] = ['account', 'access', 'commands', 'tags', 'attributes', 'puppets']

    ######################################################################
    # Player Character Options
    ######################################################################
    settings.CONTROLLERS['playercharacter'] = {
        'class': 'athanor.playercharacters.controller.PlayerCharacterController',
        'backend': 'athanor.playercharacters.controller.PlayerCharacterControllerBackend'
    }

    settings.BASE_PLAYER_CHARACTER_TYPECLASS = "athanor.playercharacters.playercharacters.DefaultPlayerCharacter"
    settings.CMDSET_PLAYER_CHARACTER = "athanor.playercharacters.cmdsets.PlayerCharacterCmdSet"

    # These restrict a player's ability to create/modify their own characters.
    # If True, only staff can perform these operations (if allowed by the privileges system)
    settings.RESTRICTED_CHARACTER_CREATION = False
    settings.RESTRICTED_CHARACTER_DELETION = False
    settings.RESTRICTED_CHARACTER_RENAME = False


    ######################################################################
    # PlaySessionDB
    ######################################################################
    settings.CONTROLLERS['playsession'] = {
        'class': 'athanor.playsessions.controller.AthanorPlaySessionController',
        'backend': 'athanor.playsessions.controller.AthanorPlaySessionControllerBackend'
    }

    settings.BASE_PLAY_SESSION_TYPECLASS = "athanor.playsessions.playsessions.DefaultPlaySession"
    settings.CMDSET_PLAYSESSION = "athanor.playsessions.cmdsets.AthanorPlaySessionCmdSet"

    ######################################################################
    # Character Settings
    ######################################################################

    # If this is enabled, characters will not see each other's true names.
    # Instead, they'll see something generic, and have to decide what to
    # call a person.
    settings.NAME_DUB_SYSTEM = False

    ######################################################################
    # Permissions
    ######################################################################

    # This dictionary describes the Evennia Permissions, including which Permissions
    # are able to grant/revoke a Permission. If a Permission is not in this dictionary,
    # then it cannot be granted through normal commands.
    # If no permission(s) is set, only the Superuser can grant it.

    settings.PERMISSION_HIERARCHY = [
        "Guest",  # note-only used if GUEST_ENABLED=True
        "Player",
        "Helper",
        "Builder",
        "Gamemaster",
        "Moderator",
        "Admin",
        "Developer",
    ]

    settings.PERMISSIONS = {
    "Helper": {
        "permission": ("Admin"),
        "description": "Those appointed to help players."
    },
    "Builder": {
        "permission": ("Admin"),
        "description": "Can edit and alter the grid, creating new Zones, Rooms, and Exits."
    },
    "Gamemaster": {
        "permission": ("Admin"),
        "description": "Can alter game-related character traits like stats, spawn items, grant rewards, puppet mobiles, etc."
    },
    "Moderator": {
        "permission": ("Admin"),
        "description": "Has access to virtually all communications tools for keeping order and enforcing social rules."
    },
    "Admin": {
        "permission": ("Developer"),
        "description": "Can make wide-spread changes to the game, administrate accounts and characters directly."
    },
    "Developer": {
        "description": "Has virtually unlimited power. Can use very dangerous commands."
    }
}


def load(settings, plugin_list):
    ######################################################################
    # Plugin Settings
    ######################################################################

    # This will hold a dictionary of plugins by their name, as reported by
    # their __init__. Failing a name, their python path will be used. The
    # values are the imported modules. The list contains them, sorted by
    # load priority.
    settings.ATHANOR_PLUGINS = dict()
    settings.ATHANOR_PLUGINS_SORTED = list()

    # convert plugin_list to a set() to eradicate duplicates. ensure that 'athanor' is included
    # as it is the core.
    plugin_set = set(plugin_list)
    plugin_set.add('athanor')

    # next, we'll import plugins.
    from importlib import import_module
    plugins_dict = dict()
    for plugin_path in plugin_set:
        found_plugin = import_module(plugin_path)
        plugin_name = getattr(found_plugin, 'PLUGIN_NAME', plugin_path)
        plugins_dict[plugin_name] = found_plugin

    settings.ATHANOR_PLUGINS_SORTED = sorted(plugins_dict.values(), key=lambda x: getattr(x, "LOAD_PRIORITY", 0))

    for plugin in settings.ATHANOR_PLUGINS_SORTED:
        if hasattr(plugin, "init_settings"):
            plugin.init_settings(settings)

    settings.ATHANOR_PLUGINS = plugins_dict
