"""
Core of the Athanor API. It is also styled as a plugin.

"""
from evennia.plugin import EvPlugin


class Athanor(EvPlugin):

    def name(self) -> str:
        return "athanor"

    def load_priority(self) -> int:
        return -100000000

    def __init__(self):
        self.styler = None
        self.controllers = None

    def integrity_check_namespaces(self):
        from athanor.identities.models import Namespace
        from django.conf import settings
        for k, v in settings.IDENTITY_NAMESPACES.items():
            nspace, created = Namespace.objects.get_or_create(db_name=k, db_prefix=v["prefix"], db_priority=v["priority"])
            if created:
                nspace.save()

    def load_styler(self):
        from evennia.utils.utils import class_from_module
        from django.conf import settings
        styler_class = class_from_module(settings.STYLER_CLASS)
        self.styler = styler_class
        self.styler.load()

    def load_controllers(self):
        from django.conf import settings
        from evennia.utils.utils import class_from_module
        self.controllers = class_from_module(settings.CONTROLLER_MANAGER_CLASS)(self)
        self.controllers.load()
        self.controllers.integrity_check()

    def at_plugin_setup(self):
        self.integrity_check_namespaces()
        self.load_styler()
        self.load_controllers()

    def init_settings(self, settings, plugins):
        from collections import defaultdict

        ######################################################################
        # Server Options
        ######################################################################

        # Let's disable that annoying timeout by default!
        settings.IDLE_TIMEOUT = -1

        # A lot of MUD-styles may want to change this to 2. Athanor's not really meant for 0 or 1 style, though.
        settings.MULTISESSION_MODE = 3

        settings.USE_TZ = True
        settings.TELNET_OOB_ENABLED = True
        settings.WEBSOCKET_ENABLED = True
        settings.INLINEFUNC_ENABLED = True

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


        ######################################################################
        # Module List Options
        ######################################################################
        # Convert LOCK_FUNC_MODULES to a list so it can be appended to by plugins.
        settings.LOCK_FUNC_MODULES = list(settings.LOCK_FUNC_MODULES)
        #settings.LOCK_FUNC_MODULES.append("athanor.lockfuncs")

        #settings.INPUT_FUNC_MODULES.append('athanor.inputfuncs')

        ######################################################################
        # Database Options
        ######################################################################
        # convert INSTALLED_APPS to a list so that plugins may append to it.
        # At this point, we can only add things after Evennia's defaults.

        settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
        settings.INSTALLED_APPS += ['athanor.logins', 'athanor.identities',
                                    'athanor.sectors', 'athanor.zones']

        ######################################################################
        # Identity and Namespaces
        ######################################################################

        settings.IDENTITY_NAMESPACES = {
            "Special": {"priority": 0, "prefix": "S"},
            "Accounts": {"priority": 100, "prefix": "A"},
            "Characters": {"priority": 200, "prefix": "C"}
        }

        settings.BASE_IDENTITY_TYPECLASS = "athanor.identities.identities.DefaultIdentity"

        ######################################################################
        # Controllers
        ######################################################################

        settings.CONTROLLER_MANAGER_CLASS = "athanor.utils.controllers.ControllerManager"
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

        settings.BASE_SECTOR_TYPECLASS = "athanor.sectors.sectors.DefaultSector"
        settings.BASE_ZONE_TYPECLASS = "athanor.zones.zones.DefaultZone"

        ######################################################################
        # Connection Options
        ######################################################################
        settings.BASE_SESSION_CLASS = "athanor.conn.session.AthanorSession"
        settings.SESSION_SYNC_ATTRS = settings.SESSION_SYNC_ATTRS + ('identity_id', 'account_identity_id')

        settings.SERVER_SESSION_HANDLER_CLASS = 'athanor.conn.sessionhandler.AthanorServerSessionHandler'

        # Command set used on the logged-in session
        #settings.CMDSET_SESSION = "athanor.serversessions.cmdsets.AthanorSessionCmdSet"

        # Command set used on session before account has logged in
        #settings.CMDSET_LOGINSCREEN = "athanor.serversessions.cmdsets.LoginCmdSet"
        #settings.CMDSET_SELECTSCREEN = 'athanor.serversessions.cmdsets.CharacterSelectScreenCmdSet'
        #settings.CMDSET_ACTIVE = 'athanor.serversessions.cmdsets.ActiveCmdSet'
        #settings.BASE_SERVER_SESSION_TYPECLASS = "athanor.serversessions.serversessions.DefaultServerSession"


        #settings.EXAMINE_HOOKS['session'] = []

        #settings.SESSION_SYNC_ATTRS = list(settings.SESSION_SYNC_ATTRS)

        ######################################################################
        # Account Options
        ######################################################################
        #settings.BASE_ACCOUNT_TYPECLASS = "athanor.accounts.typeclasses.AthanorAccount"
        #settings.CONTROLLERS['account'] = 'athanor.accounts.controller.AthanorAccountController'

        # Command set for accounts with or without a character (ooc)
        #settings.CMDSET_ACCOUNT = "athanor.accounts.cmdsets.AccountCmdSet"

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
        # Character Options
        ######################################################################
        #settings.CONTROLLERS['character'] = 'athanor.characters.controller.CharacterController'

        #settings.BASE_CHARACTER_TYPECLASS = "athanor.characters.characters.DefaultCharacter"
        #settings.CMDSET_PLAYER_CHARACTER = "athanor.characters.cmdsets.CharacterCmdSet"

        # These restrict a player's ability to create/modify their own characters.
        # If True, only staff can perform these operations (if allowed by the privileges system)
        settings.RESTRICTED_CHARACTER_CREATION = False
        settings.RESTRICTED_CHARACTER_DELETION = False
        settings.RESTRICTED_CHARACTER_RENAME = False

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
