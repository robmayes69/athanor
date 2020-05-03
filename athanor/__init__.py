"""
Core of the Athanor API. It is also styled as a plugin.

"""

# This dictionary will be filled in with useful singletons as the system loads.

_API_STORAGE = dict()

# The Core must always load first.
LOAD_PRIORITY = -100000000

PLUGIN_NAME = 'athanor'

LOADED = False


def _init():

    pspace_dict = dict()
    def get_or_create_pspace(pspace):
        if pspace in pspace_dict:
            return pspace_dict[pspace]
        model, created = Pluginspace.objects.get_or_create(db_name=pspace)
        if created:
            model.save()
        pspace_dict[pspace] = model
        return model

    global LOADED, _API_STORAGE
    if LOADED:
        return

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

    manager = class_from_module(settings.CONTROLLER_MANAGER_CLASS)()
    _API_STORAGE['controller_manager'] = manager
    manager.load()

    # Setting this true so that integrity checks will not call _init() again.
    LOADED = True

    entity_con = manager.get('entity')
    entity_con.check_integrity()




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
    # the keys are the objects that it applies to, such as 'account' or 'avatar'. This is separate
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
    # Controllers
    ######################################################################

    settings.CONTROLLER_MANAGER_CLASS = "athanor.utils.controllers.ControllerManager"
    settings.BASE_CONTROLLER_CLASS = "athanor.utils.controllers.AthanorController"
    settings.CONTROLLERS = dict()

    ######################################################################
    # Asset Loading
    ######################################################################
    settings.CONTROLLERS['asset'] = {
        'class': 'athanor.utils.assets.AssetController',
        'backend': 'athanor.utils.assets.AssetControllerBackend'
    }
    settings.ASSET_LOADER_CLASS = 'athanor.utils.assets.PluginAssetLoader'

    settings.ENTITY_TYPECLASSES = {
        'dimension': 'athanor.entities.entities.DefaultDimension',
        'sector': 'athanor.entities.entities.DefaultSector',
        'room': 'athanor.entities.entities.AthanorRoom',
        'exit': 'athanor.entities.entities.AthanorExit',
        'gateway': 'athanor.entities.entities.DefaultGateway',
    }

    settings.ENTITY_CREATION_MAP = {
        'name': '_create_name',
        'command': '_create_command',
        'identity': '_create_identity',
        'inventory': '_create_inventory',
        'equip': '_create_equip',
        'dimension': '_create_dimension',
        'sector': '_create_sector',
        'structure': '_create_structure',
        'room': '_create_room',
        'gateway': '_create_gateway',
        'exit': '_create_exit',
        'fixture': '_create_fixture'
    }

    ######################################################################
    # Access Control List System
    ######################################################################
    # These two settings contain key-path combinations.
    settings.ACL_IDENTITY_HANDLER_CLASSES = dict()

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
    settings.PORTAL_SESSION_HANDLER_CLASS = 'athanor.utils.portalsessionhandler.AthanorPortalSessionHandler'
    settings.EXAMINE_HOOKS['session'] = []

    settings.SESSION_SYNC_ATTRS = list(settings.SESSION_SYNC_ATTRS)
    #settings.SESSION_SYNC_ATTRS.extend(["pcid", "pcname"])

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
    # Identity Options
    ######################################################################
    settings.CONTROLLERS['identity'] = {
        'class': 'athanor.identities.controller.IdentityController',
        'backend': 'athanor.identities.controller.IdentityControllerBackend'
    }

    settings.IDENTITY_NAMESPACES = [
        "system",
        "pc",
        "npc",

    ]

    # This should basically never be used, but has to in order to satisfy the Typeclass system.
    settings.BASE_IDENTITY_TYPECLASS = "athanor.identities.identities.DefaultIdentity"

    ######################################################################
    # Player Character Options
    ######################################################################
    settings.BASE_PLAYER_CHARACTER_TYPECLASS = "athanor.playercharacters.playercharacters.DefaultPlayerCharacter"
    #settings.CMDSET_PLAYER_CHARACTER = "athanor.playercharacters.cmdsets.AthanorPlayerCharacterCmdSet"

    # These restrict a player's ability to create/modify their own characters.
    # If True, only staff can perform these operations (if allowed by the privileges system)
    settings.RESTRICTED_CHARACTER_CREATION = False
    settings.RESTRICTED_CHARACTER_DELETION = False
    settings.RESTRICTED_CHARACTER_RENAME = False

    settings.ACL_IDENTITY_HANDLER_CLASSES['player'] = 'athanor.identities.utils.PlayerACLIdentityHandler'

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
    # Grid Settings
    ######################################################################
    settings.CONTROLLERS['dimension'] = {
        'class': 'athanor.dimensions.controller.DimensionController',
        'backend': 'athanor.dimensions.controller.DimensionControllerBackend'
    }

    settings.CONTROLLERS['sector'] = {
        'class': 'athanor.sectors.controller.SectorController',
        'backend': 'athanor.sectors.controller.SectorControllerBackend'
    }

    settings.CONTROLLERS['entity'] = {
        'class': 'athanor.entities.controller.EntityController',
        'backend': 'athanor.entities.controller.EntityControllerBackend'
    }

    settings.BASE_DIMENSION_TYPECLASS = 'athanor.dimensions.dimensions.DefaultDimension'
    settings.BASE_SECTOR_TYPECLASS = 'athanor.sectors.sectors.DefaultSector'
    settings.BASE_ENTITY_TYPECLASS = 'athanor.entities.entities.DefaultEntity'
    settings.BASE_ROOM_TYPECLASS = 'athanor.rooms.rooms.AthanorRoom'
    settings.BASE_EXIT_TYPECLASS = 'athanor.exits.exits.AthanorExit'

    ######################################################################
    # Inventory Settings
    ######################################################################
    settings.BASE_INVENTORY_TYPECLASS = 'athanor.inventories.inventories.DefaultInventory'

    ######################################################################
    # Equip Settings
    ######################################################################
    settings.BASE_EQUIP_TYPECLASS = 'athanor.equips.equips.DefaultEquip'

    ######################################################################
    # Avatar Settings
    ######################################################################

    settings.CMDSET_AVATAR = "athanor.grid.cmdsets.AthanorAvatarCmdSet"
    settings.BASE_AVATAR_TYPECLASS = "athanor.grid.typeclasses.AthanorAvatar"

    settings.EXAMINE_HOOKS['avatar'] = ['character', 'puppeteer', 'access', 'commands', 'scripts', 'tags', 'attributes', 'contents']

    # If this is enabled, characters will not see each other's true names.
    # Instead, they'll see something generic, and have to decide what to
    # call a person.
    settings.NAME_DUB_SYSTEM = False

    ######################################################################
    # BBS Settings
    ######################################################################
    settings.BASE_BBS_BOARD_TYPECLASS = 'athanor.bbs.boards.DefaultBoard'
    settings.BASE_BBS_POST_TYPECLASS = 'athanor.bbs.posts.DefaultPost'


    ######################################################################
    # Grid / Building Settings
    ######################################################################

    #settings.BASE_ROOM_TYPECLASS = "athanor.grid.typeclasses.AthanorRoom"
    #settings.BASE_EXIT_TYPECLASS = "athanor.grid.typeclasses.AthanorExit"
    #settings.BASE_OBJECT_TYPECLASS = "athanor.grid.typeclasses.AthanorItem"

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
        "description": "Can edit and alter the grid, creating new rooms and areas."
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
